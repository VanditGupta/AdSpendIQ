#!/bin/bash
# Load environment variables from .env file
# This script handles comments and empty lines properly

while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        # Export the variable
        export "$line"
    fi
done < .env

echo "Environment variables loaded successfully!"
echo "SNOWFLAKE_ACCOUNT: $SNOWFLAKE_ACCOUNT"
echo "SNOWFLAKE_USER: $SNOWFLAKE_USER"
echo "SNOWFLAKE_DATABASE: $SNOWFLAKE_DATABASE"
echo "SNOWFLAKE_SCHEMA: $SNOWFLAKE_SCHEMA"
