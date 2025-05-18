from solana.rpc.api import Client
from solders.keypair import Keypair
import json
import os
import time
import requests

# Use a more reliable RPC endpoint
RPC_ENDPOINTS = [
    "https://api.devnet.solana.com",
    "https://devnet.solana.com",
    "https://devnet.genesysgo.net",
    "https://devnet.api.rpcpool.com"
]

# Initialize with first endpoint
current_endpoint_index = 0
client = Client(RPC_ENDPOINTS[current_endpoint_index])

def switch_rpc_endpoint():
    """Switch to next RPC endpoint if current one fails"""
    global client, current_endpoint_index
    current_endpoint_index = (current_endpoint_index + 1) % len(RPC_ENDPOINTS)
    new_endpoint = RPC_ENDPOINTS[current_endpoint_index]
    print(f"Switching RPC endpoint to: {new_endpoint}")
    client = Client(new_endpoint)

def generate_keypair():
    """Generate a new Solana keypair"""
    return Keypair()

def save_keypair(keypair: Keypair, filename: str):
    """Save a keypair to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(list(bytes(keypair)), f)

def request_airdrop(pubkey, amount: float = 0.5) -> str:
    """Request SOL from the devnet faucet"""
    global client
    print(f"Requesting {amount} SOL from devnet faucet...")
    
    # Try multiple times with different amounts
    amounts_to_try = [0.5, 0.5, 0.5]  # Try 0.5 SOL multiple times instead of larger amounts
    
    for try_amount in amounts_to_try:
        try:
            print(f"Trying to request {try_amount} SOL...")
            # Try the RPC airdrop first
            response = client.request_airdrop(pubkey, int(try_amount * 1_000_000_000))
            if response.value:
                print(f"Successfully requested {try_amount} SOL")
                return response.value
        except Exception as e:
            print(f"RPC airdrop failed for {try_amount} SOL: {e}")
            # Switch RPC endpoint on failure
            switch_rpc_endpoint()
            time.sleep(2)  # Wait before next attempt
    
    # If RPC airdrop fails, try the public faucet
    for try_amount in amounts_to_try:
        try:
            print(f"Trying public faucet for {try_amount} SOL...")
            url = f"https://api.devnet.solana.com/airdrop/{pubkey}/{int(try_amount * 1_000_000_000)}"
            response = requests.post(url)
            if response.status_code == 200:
                print(f"Successfully requested {try_amount} SOL from public faucet")
                return response.json()["signature"]
        except Exception as e:
            print(f"Public faucet request failed for {try_amount} SOL: {e}")
            time.sleep(2)  # Wait before next attempt
    
    raise Exception("Failed to request airdrop from both RPC and public faucet")

def wait_for_confirmation(signature: str, max_retries: int = 30):
    """Wait for transaction confirmation"""
    global client
    print(f"Waiting for confirmation of signature: {signature}")
    for i in range(max_retries):
        try:
            response = client.get_signature_statuses([signature])
            if response.value[0] is not None:
                print("Transaction confirmed!")
                return True
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(2)  # Increased wait time
        except Exception as e:
            print(f"Error checking confirmation: {e}")
            switch_rpc_endpoint()
            time.sleep(2)
    return False

def get_balance(pubkey) -> float:
    """Get the balance of an account in SOL"""
    global client
    try:
        response = client.get_balance(pubkey)
        return response.value / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        print(f"Error getting balance, switching RPC endpoint: {e}")
        switch_rpc_endpoint()
        response = client.get_balance(pubkey)
        return response.value / 1_000_000_000

def main():
    print("Solana Devnet Faucet Account Generator")
    print("-------------------------------------")
    print("This tool will:")
    print("1. Generate new Solana keypairs")
    print("2. Save them to JSON files")
    print("3. Request initial airdrops")
    print("4. Verify balances")
    print("\nNote: Each account will receive 0.5 SOL initially")
    print("      You can request more SOL later using sol.py")
    print("-------------------------------------")
    
    # Create faucets directory if it doesn't exist
    if not os.path.exists('faucets'):
        os.makedirs('faucets')
        print("Created 'faucets' directory")
    
    # Get number of accounts to generate
    while True:
        try:
            num_accounts = int(input("\nHow many faucet accounts do you want to generate? "))
            if num_accounts <= 0:
                print("Please enter a positive number")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    print(f"\nGenerating {num_accounts} faucet accounts...")
    
    # Generate accounts
    for i in range(num_accounts):
        try:
            print(f"\nProcessing account {i+1}/{num_accounts}...")
            
            # Generate and save keypair
            keypair = generate_keypair()
            filename = f"faucets/faucet_{i+1}.json"
            save_keypair(keypair, filename)
            print(f"Generated and saved keypair to {filename}")
            
            # Request airdrop
            print("Requesting initial airdrop...")
            signature = request_airdrop(keypair.pubkey())
            
            # Wait for confirmation
            if wait_for_confirmation(signature):
                # Check balance
                balance = get_balance(keypair.pubkey())
                print(f"Account balance: {balance} SOL")
                
                # If balance is low, try one more airdrop
                if balance < 0.5:
                    print("Balance is low, requesting additional airdrop...")
                    time.sleep(5)  # Wait before requesting another airdrop
                    signature = request_airdrop(keypair.pubkey())
                    if wait_for_confirmation(signature):
                        final_balance = get_balance(keypair.pubkey())
                        print(f"Final balance: {final_balance} SOL")
            else:
                print("Failed to confirm airdrop")
            
            # Wait between accounts to avoid rate limits
            if i < num_accounts - 1:  # Don't wait after the last account
                print("Waiting 5 seconds before next account...")
                time.sleep(5)
            
        except Exception as e:
            print(f"Error processing account {i+1}: {e}")
            continue
    
    print("\nFaucet account generation complete!")
    print("\nTo use these accounts:")
    print("1. Copy one of the generated JSON files to 'faucet.json' in this directory")
    print("2. Run 'sol.py' to send SOL from the selected account")
    print("\nNote: Keep your faucet.json files secure as they contain private keys")

if __name__ == "__main__":
    main() 