"""Producer-consumer tasks communicating via async queue."""
from common.app import application_entrypoint
from common.examples.asyncq import Application, application_config


def main():
    """The main entry point of the application"""
    application_entrypoint(Application, application_config)


if __name__ == "__main__":
    main()
