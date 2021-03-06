#!/usr/bin/python
# coding=utf-8
################################################################################

from __future__ import with_statement

from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import Mock
from mock import patch

from diamond.collector import Collector
from conntrack import ConnTrackCollector

################################################################################


class TestConnTrackCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('ConnTrackCollector', {
            'interval': 10,
            'bin': 'true',
        })

        self.collector = ConnTrackCollector(config, None)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_synthetic_data(self, publish_mock):
        with patch('subprocess.Popen.communicate', Mock(return_value=(
            'net.netfilter.nf_conntrack_count = 33', '')
        )):
            self.collector.collect()

        metrics = {
            'nf_conntrack_count': 33.0
        }

        self.setDocExample(collector=self.collector.__class__.__name__,
                           metrics=metrics,
                           defaultpath=self.collector.config['path'])
        self.assertPublishedMany(publish_mock, metrics)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_fail_gracefully(self, publish_mock):
        with patch('subprocess.Popen.communicate', Mock(return_value=(
            'sysctl: cannot stat /proc/sys/net/netfilter/nf_conntrack_count: '
            + 'No such file or directory', '')
        )):
            self.collector.collect()

        self.assertPublishedMany(publish_mock, {})

    @patch('os.access', Mock(return_value=False))
    @patch.object(Collector, 'publish')
    def test_should_fail_gracefully_2(self, publish_mock):
        self.collector.collect()
        self.assertPublishedMany(publish_mock, {})

################################################################################
if __name__ == "__main__":
    unittest.main()
