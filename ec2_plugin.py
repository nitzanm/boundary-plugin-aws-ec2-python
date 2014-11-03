import boto
import boto.ec2
import sys
from itertools import chain

from boundary_aws_plugin.cloudwatch_plugin import CloudwatchPlugin
from boundary_aws_plugin.cloudwatch_metrics import CloudwatchMetrics


class Ec2CloudwatchMetrics(CloudwatchMetrics):
    def __init__(self, access_key_id, secret_access_key):
        return super(Ec2CloudwatchMetrics, self).__init__(access_key_id, secret_access_key, 'AWS/EC2')

    def get_region_list(self):
        # Some regions are returned that actually do not support EC2.  Skip those.
        return [r for r in boto.ec2.regions() if r.name not in ['cn-north-1', 'us-gov-west-1']]

    def get_entities_for_region(self, region):
        ec2 = boto.connect_ec2(self.access_key_id, self.secret_access_key, region=region)
        return list(chain(*(r.instances for r in ec2.get_all_instances())))

    def get_entity_dimensions(self, region, instance):
        return dict(InstanceId=instance.id)

    def get_entity_source_name(self, instance):
        return instance.id

    def get_metric_list(self):
        return (
            ('CPUCreditUsage', 'Average', 'AWS_EC2_CPU_CREDIT_USAGE'),
            ('CPUCreditBalance', 'Average', 'AWS_EC2_CPU_CREDIT_BALANCE'),
            ('CPUUtilization', 'Average', 'AWS_EC2_CPU_UTILIZATION', 0.01),
            ('DiskReadOps', 'Sum', 'AWS_EC2_DISK_READ_OPS'),
            ('DiskWriteOps', 'Sum', 'AWS_EC2_DISK_WRITE_OPS'),
            ('DiskReadBytes', 'Sum', 'AWS_EC2_DISK_READ_BYTES'),
            ('DiskWriteBytes', 'Sum', 'AWS_EC2_DISK_WRITE_BYTES'),
            ('NetworkIn', 'Sum', 'AWS_EC2_NETWORK_IN'),
            ('NetworkOut', 'Sum', 'AWS_EC2_NETWORK_OUT'),
            ('StatusCheckFailed', 'Average', 'AWS_EC2_STATUS_CHECK_FAILED'),
            ('StatusCheckFailed_Instance', 'Average', 'AWS_EC2_STATUS_CHECK_FAILED_INSTANCE'),
            ('StatusCheckFailed_System', 'Average', 'AWS_EC2_STATUS_CHECK_FAILED_SYSTEM'),
        )


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        import logging
        logging.basicConfig(level=logging.INFO)

    plugin = CloudwatchPlugin(Ec2CloudwatchMetrics, 'NM_', 'boundary-plugin-aws-ec2-python-status')
    plugin.main()

