#!/bin/bash
# Cleanup old rake log files

cd ~/tilden_test/rake_test

# Count log files
LOG_COUNT=$(ls -1 rake_log_*.csv 2>/dev/null | wc -l)

if [ "$LOG_COUNT" -eq 0 ]; then
    echo "No log files found to delete"
    exit 0
fi

echo "Found $LOG_COUNT log files"
echo "Total size: $(du -sh rake_log_*.csv 2>/dev/null | awk '{sum+=$1} END {print sum}') KB"

# Show first few and last few
echo -e "\nFirst 5 logs:"
ls -lh rake_log_*.csv 2>/dev/null | head -5

echo -e "\nLast 5 logs:"
ls -lh rake_log_*.csv 2>/dev/null | tail -5

# Ask for confirmation
read -p "Delete all $LOG_COUNT log files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f rake_log_*.csv
    echo "✅ Deleted $LOG_COUNT log files"
else
    echo "Cancelled - no files deleted"
fi
