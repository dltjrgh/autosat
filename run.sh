DIR = $1
BENCHS=$(ls $DIR)

for bench in $BENCHS; do
    echo Run $DIR/$bench
    echo output $bench.log
    easysat/Easysat $DIR/$bench > benchmarks/output/$bench.log
done