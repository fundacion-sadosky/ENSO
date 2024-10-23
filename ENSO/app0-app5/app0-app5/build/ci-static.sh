echo "===================================="
echo "CI STATIC ANALYSIS: app0-app5"
echo "===================================="
code=0
python3 -m ruff app0-app5/src
code+=$?
if [ $code -gt 0 ]
then
  echo "[FAILED] CI STATIC ANALYSIS: app0-app5"
fi
echo "========================================================================================================"
exit $code
