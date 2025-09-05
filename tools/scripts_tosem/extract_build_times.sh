# Extracts build times from a MAGMA experiment folder
# the first argument should be the parent directory to the
# `ar`, `log`, `poc` folders


if [ "$#" -ne 1 ]; then
	echo "Usage: $0 technique-results-dir"
	echo "We expect technique-results-dir to be a dir containing ar/log/poc folder,
	whose basename is the name of a fuzzer technique. We assume the contents
	in log start with that fuzzer technique, i.e. TECH=aflgo, <technique-results-dir>
	is /some/stuff/aflgo, log contains files 'aflgo_*.log'."
	exit 1
fi

resdir=$1
technique=`basename $resdir`
logdir=$resdir/log

for buildlog in $logdir/*_build.log; do
	buildlog_name=`basename $buildlog`
	# first we strip the technique
	benchmark_name="${buildlog_name/${technique}_/}"
	# then strip build.log
	benchmark_name="${benchmark_name/_build.log/}"
	build_time=`grep "#29 DONE" $buildlog| sed 's/#29 DONE \(.*\)s/\1/'`
	cached_time=`grep "#29 CACHED" $buildlog`
	if [ ! -z "$cached_time" ]; then
		echo "for $benchmark_name, build is cached; can't extract time" >> /dev/stderr
		echo "$benchmark_name,CACHED"
	else
		echo "$benchmark_name,$build_time"
	fi
done

