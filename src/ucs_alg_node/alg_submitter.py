from src.ucs_alg_node import cli

MODE_MQ = 'mq'
MODE_DB = 'db'
MODE_API = 'api'


class AlgSubmitter:
    def __init__(self, dest, mode, username, passwd, topic):
        self.dest = dest
        self.mode = mode
        self.username = username
        self.passwd = passwd
        self.topic = topic

        output_type = dest.split(':')[0]
        self.output_type = output_type
        if 'http' in output_type:
            self.mode = MODE_API
            self.submit_cli = cli.HttpCli(dest, '')
        elif 'mqtt' in output_type:
            self.mode = MODE_MQ
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_cli = cli.MqttCli(host, port, self.username, self.passwd, [self.topic])
        elif 'redis' in output_type:
            self.mode = MODE_DB
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_cli = cli.RedisCli(host, port, 0, self.username, self.passwd)
            # TODO redis im mq mode
            # if self.mode == MODE_DB:
            # elif self.mode == MODE_MQ:
            #     self.submit_cli = cli.RedisCli(dest, self.username, self.passwd)
        elif 'nsq' in output_type:
            self.mode = MODE_MQ
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_mode = cli.MqCli(host, port, self.topic, 0, self.username, self.passwd)
        else:
            self.submit_cli = None

        self.cli = None

    def submit(self, tid, result):
        """
        submit result to server
        :return 0 if success, -1 if failed
        """
        if not self.cli:
            return -1
        else:
            if self.output_type == 'http':
                return self.cli.submit(tid, result)
            elif self.output_type == 'mqtt':
                return self.cli.publish(self.topic, {
                    'tid': tid,
                    'res': result
                })
            elif self.output_type == 'redis':
                return self.cli.set(tid, result)
            elif self.output_type == 'nsq':
                return self.cli.publish({
                    'tid': tid,
                    'res': result
                })
            else:
                return -1
