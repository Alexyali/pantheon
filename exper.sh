rm -rf result/* && mkdir result/drive-LTE && mkdir result/PDF
src/experiments/test.py local --schemes "cubic vegas bbr cldcc" \
--uplink-trace traces/ATT-LTE-driving-2016.down \
--downlink-trace traces/ATT-LTE-driving-2016.down \
--append-mm-cmds "--uplink-queue=droptail --uplink-queue-args="packets=200"" \
--data-dir result/drive-LTE --run-times 1 -t 60 --random-order &&
src/analysis/analyze.py --data-dir result/drive-LTE &&
cp result/drive-LTE/pantheon_report.pdf result/PDF/drive-LTE_report.pdf

clear && mkdir result/walk-LTE
src/experiments/test.py local --schemes "cubic vegas bbr cldcc" \
--uplink-trace traces/trace-1553189663-ts-walking \
--downlink-trace traces/trace-1553189663-ts-walking \
--append-mm-cmds "--uplink-queue=droptail --uplink-queue-args="packets=200"" \
--data-dir result/walk-LTE --run-times 1 -t 60 --random-order &&
src/analysis/analyze.py --data-dir result/walk-LTE &&
cp result/walk-LTE/pantheon_report.pdf result/PDF/walk-LTE_report.pdf