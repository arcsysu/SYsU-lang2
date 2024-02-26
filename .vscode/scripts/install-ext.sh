#!/bin/bash

echo "安装当前工作区所有推荐的VSCode扩展组件..."

# check whether jq is installed, if not, for macOS, use brew to install it, for linux, use apt-get to install it, or use yum to install it
if ! [ -x "$(command -v jq)" ]; then
    echo "Error: jq is not installed." >&2
    if [ -x "$(command -v brew)" ]; then
        echo "Installing jq using brew..."
        brew install jq
    elif [ -x "$(command -v apt-get)" ]; then
        echo "Installing jq using apt-get..."
        sudo apt-get install jq
    elif [ -x "$(command -v yum)" ]; then
        echo "Installing jq using yum..."
        sudo yum install jq
    else
        echo "Error: jq is not installed, and we don't know how to install it." >&2
        exit 1
    fi
fi


# Assuming extensions.json is in the parent directory
json=$(<../extensions.json)
recommendations=$(echo "$json" | jq -r '.recommendations[]')

for extension in $recommendations; do
    echo code --install-extension "$extension"
done