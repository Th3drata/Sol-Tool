# Solana Devnet Tools

A collection of Python tools for interacting with the Solana Devnet, including faucet management and SOL transfer capabilities. These tools are designed to be reliable and user-friendly, with automatic RPC endpoint switching and robust error handling.

## Features

- Generate multiple Solana faucet accounts
- Automatic RPC endpoint switching for reliability
- Multiple airdrop attempts with different amounts
- Robust error handling and transaction confirmation
- Automatic faucet management with fallback options
- Interactive command-line interface

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Th3drata/Sol-Tool.git.git
cd solana_tools
```

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
solana_tools/
├── README.md
├── requirements.txt
├── sol.py              # SOL transfer tool
├── generate_faucets.py # Faucet account generator
├── faucet.json         # Current active faucet
└── faucets/           # Directory for additional faucets
    ├── faucet_1.json
    ├── faucet_2.json
    └── ...
```

## Tools

### 1. Generate Faucet Accounts (`generate_faucets.py`)

This tool generates multiple Solana faucet accounts and requests initial airdrops for each.

Usage:
```bash
python generate_faucets.py
```

Features:
- Generates specified number of keypairs
- Saves keypairs to JSON files
- Requests initial airdrops (0.5 SOL each)
- Verifies balances after airdrops
- Provides detailed progress information
- Automatic RPC endpoint switching
- Multiple airdrop attempts if needed

### 2. SOL Transfer Tool (`sol.py`)

A robust tool for sending SOL on the Solana Devnet with automatic faucet management.

Usage:
```bash
python sol.py
```

Features:
- Interactive command-line interface
- Validates wallet addresses
- Automatic faucet selection with sufficient balance
- Multiple airdrop attempts with different amounts
- Transaction confirmation monitoring
- Detailed error reporting
- Automatic RPC endpoint switching

## How It Works

### RPC Endpoint Management

The system uses multiple RPC endpoints for reliability:
- Automatically switches between endpoints on failure
- Includes fallback endpoints
- Handles rate limiting and timeouts

### Faucet Management

The system uses a multi-tier approach for faucet management:

1. Primary Faucet (`faucet.json`):
   - The main faucet account used for transactions
   - Automatically tries to get airdrops if balance is insufficient

2. Backup Faucets (`faucets/` directory):
   - Additional faucet accounts for redundancy
   - Automatically checked when primary faucet has insufficient balance

### Airdrop Process

The system implements a robust airdrop request process:

1. Tries multiple amounts (0.5 SOL)
2. Attempts RPC airdrop first
3. Falls back to public faucet if RPC fails
4. Includes retry logic and confirmation checks
5. Switches RPC endpoints on failure

### Transaction Process

1. Validates destination address
2. Finds faucet with sufficient balance
3. Creates and signs transaction
4. Sends transaction and monitors confirmation
5. Provides detailed status updates

## Error Handling

The tools include comprehensive error handling for:
- Invalid wallet addresses
- Insufficient balances
- Failed airdrops
- Transaction failures
- Network issues
- RPC endpoint failures

## Best Practices

1. Always verify wallet addresses before sending
2. Keep multiple faucet accounts for redundancy
3. Monitor transaction confirmations
4. Use appropriate amounts for airdrops
5. Handle errors gracefully
6. Keep faucet files secure

## Security Notes

- Never share your private keys
- Keep faucet.json and faucets directory secure
- Use virtual environments for isolation
- Regularly update dependencies
- Monitor account balances

## Troubleshooting

Common issues and solutions:

1. Insufficient Balance:
   - System will automatically try to get airdrops
   - Check faucet balances using the tools
   - Try using a different faucet account

2. Airdrop Failures:
   - System will retry with different amounts
   - Check network connectivity
   - Verify Devnet status
   - System will switch RPC endpoints

3. Transaction Failures:
   - Verify destination address
   - Check transaction confirmation status
   - Ensure sufficient balance for fees
   - Check RPC endpoint status

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub

## Acknowledgments

- Solana Foundation for the Devnet
- Python Solana SDK contributors
- Community members and contributors 
