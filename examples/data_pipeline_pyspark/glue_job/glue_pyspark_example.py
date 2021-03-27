import argparse
import logging

from pyspark.sql import SparkSession

logging.basicConfig(level=logging.DEBUG)


def main():
    logging.info("starting pyspark example")

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--destination", type=str, required=True)

    args, unknown = parser.parse_known_args()

    logging.info(f"args parsed : {args}")
    logging.info(
        f"the args passed by glue by default are in the unknown variable {unknown}"
    )

    source = args.source
    destination = args.destination

    # init spark context and session
    spark = SparkSession.builder.appName(__file__).getOrCreate()

    # read data and write back to s3
    df = _read_from_source(spark, source)
    df.show()
    _write_to_destination(df, destination)
    logging.info("finished pyspark example.")
    return df


def _read_from_source(spark, source):
    logging.debug(f"source: {source}")
    return spark.read.csv(source)


def _write_to_destination(df, destination, mode="overwrite"):
    logging.debug(f"destination: {destination}")
    df.write.csv(destination, mode=mode)


if __name__ == "__main__":
    main()
