from data_pipeline_with_packaged_project.glue_helper import some_helper_class


def main():
    some_helper_class()
    print(f"hello world from {__file__} !")


if __name__ == "__main__":
    main()
