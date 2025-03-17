#!/bin/bash

# Define the folder name
FOLDER="Environment-Scripts"

# Check if the folder exists
if [ -d "$FOLDER" ]; then
    echo "✅ Found folder: $FOLDER"
    echo "🔄 Making all files in $FOLDER executable..."

    # Apply execute permission to all files inside the folder
    chmod +x "$FOLDER"/*

    echo "✅ All files in $FOLDER are now executable!"
else
    echo "❌ Folder '$FOLDER' not found! Please check the directory name."
    exit 1
fi
