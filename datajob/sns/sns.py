from typing import Union

from aws_cdk import aws_sns
from aws_cdk import aws_sns_subscriptions
from aws_cdk import core
from aws_cdk.core import Arn
from aws_cdk.core import ArnComponents

from datajob.datajob_base import DataJobBase


class SnsTopic(DataJobBase):
    def __init__(
        self,
        datajob_stack: core.Construct,
        name: str,
        notification: Union[str, list],
        **kwargs
    ):
        """
        :param datajob_stack: aws cdk core construct object.
        :param name: name for the SNS Topic.
        :param notification: email address as string or list of email addresses to be subscribed.
        :param kwargs:
        """
        super().__init__(datajob_stack, name, **kwargs)
        self.notification = notification
        self.sns_topic = None

    def create(self):
        self.sns_topic = aws_sns.Topic(
            scope=self,
            id=self.unique_name,
            display_name=self.unique_name,
            topic_name=self.unique_name,
        )
        self.add_email_subscription()

    def add_email_subscription(self) -> None:
        """Add an email or a list of emails as subscribers to a topic.

        :param sns_topic: an SNS Topic instance of aws cdk
        :param notification: email address as string or list of email addresses to be subscribed.
        :return: None
        """
        if isinstance(self.notification, list):
            for email in self.notification:
                self.sns_topic.add_subscription(
                    aws_sns_subscriptions.EmailSubscription(email)
                )
        else:
            self.sns_topic.add_subscription(
                aws_sns_subscriptions.EmailSubscription(self.notification)
            )

    def get_topic_arn(self) -> str:
        """The ARN will be formatted as follows:

        arn:{partition}:{service}:{region}:{account}:{resource}{sep}{resource-name}
        :return: return a well formatted arn string
        """
        arn_components = ArnComponents(
            partition="aws",
            service="sns",
            region=self.datajob_stack.env.region,
            account=self.datajob_stack.env.account,
            resource=self.unique_name,
        )
        return Arn.format(components=arn_components, stack=self.datajob_stack)
