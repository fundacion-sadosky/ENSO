echo "========================================================================================================"
echo "CI STATIC ANALYSIS: platform-auth"
echo "========================================================================================================"
code=0
python3 -m ruff plugins/platform-auth/src
code+=$?

if [ $code -gt 0 ]
then
  echo "[FAILED] CI STATIC ANALYSIS: platform-auth"
fi
echo "========================================================================================================"
exit $code
