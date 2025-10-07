#!/bin/bash
# Clean up old/empty log files from failed attempts
# Keep only files larger than 10KB (real data)

cd ~/tilden_test/rake_test

echo "=== Finding small/empty log files to remove ==="
find . -name "rake_log_*.csv" -type f -size -10k -ls

echo ""
echo "=== Removing small/empty log files ==="
find . -name "rake_log_*.csv" -type f -size -10k -delete

echo ""
echo "=== Remaining log files ==="
ls -lht rake_log_*.csv | head -10

echo ""
echo "✓ Cleanup complete!"
