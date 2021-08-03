import argparse
import random

import boto3

try:  # python3
    from urllib.request import urlretrieve
except:  # python2
    from urllib import urlretrieve


region = boto3.Session().region_name
prefix = "sagemaker/DEMO-xgboost-regression"


def data_split(
    FILE_DATA,
    FILE_TRAIN,
    FILE_VALIDATION,
    FILE_TEST,
    PERCENT_TRAIN,
    PERCENT_VALIDATION,
    PERCENT_TEST,
):
    data = [l for l in open(FILE_DATA, "r")]
    train_file = open(FILE_TRAIN, "w")
    valid_file = open(FILE_VALIDATION, "w")
    tests_file = open(FILE_TEST, "w")

    num_of_data = len(data)
    num_train = int((PERCENT_TRAIN / 100.0) * num_of_data)
    num_valid = int((PERCENT_VALIDATION / 100.0) * num_of_data)
    num_tests = int((PERCENT_TEST / 100.0) * num_of_data)

    data_fractions = [num_train, num_valid, num_tests]
    split_data = [[], [], []]

    rand_data_ind = 0

    for split_ind, fraction in enumerate(data_fractions):
        for i in range(fraction):
            rand_data_ind = random.randint(0, len(data) - 1)
            split_data[split_ind].append(data[rand_data_ind])
            data.pop(rand_data_ind)

    for l in split_data[0]:
        train_file.write(l)

    for l in split_data[1]:
        valid_file.write(l)

    for l in split_data[2]:
        tests_file.write(l)

    train_file.close()
    valid_file.close()
    tests_file.close()


def write_to_s3(fobj, bucket, key):
    return (
        boto3.Session(region_name=region)
        .resource("s3")
        .Bucket(bucket)
        .Object(key)
        .upload_fileobj(fobj)
    )


def upload_to_s3(url, filename):
    fobj = open(filename, "rb")
    bucket, key = url.replace("s3://", "").split("/", 1)
    write_to_s3(fobj, bucket, key)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, required=True)
    parser.add_argument("--validation", type=str, required=True)
    parser.add_argument("--test", type=str, required=True)

    args, unknown = parser.parse_known_args()

    train_path = args.train
    validation_path = args.validation
    test_path = args.test

    FILE_TRAIN = train_path.split("/")[-1]
    print(f"FILE_TRAIN {FILE_TRAIN}")
    FILE_VALIDATION = validation_path.split("/")[-1]
    print(f"FILE_VALIDATION {FILE_VALIDATION}")
    FILE_TEST = test_path.split("/")[-1]
    print(f"test_file_name {FILE_TEST}")

    # Load the dataset
    FILE_DATA = "abalone"
    urlretrieve(
        "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/regression/abalone",
        FILE_DATA,
    )

    PERCENT_TRAIN = 70
    PERCENT_VALIDATION = 15
    PERCENT_TEST = 15
    data_split(
        FILE_DATA,
        FILE_TRAIN,
        FILE_VALIDATION,
        FILE_TEST,
        PERCENT_TRAIN,
        PERCENT_VALIDATION,
        PERCENT_TEST,
    )

    # upload the files to the S3 bucket
    upload_to_s3(train_path, FILE_TRAIN)
    upload_to_s3(validation_path, FILE_VALIDATION)
    upload_to_s3(test_path, FILE_TEST)
