#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <csignal>
#include <cstring>
#if _AIX
#include <unistd.h>
#endif
#include <librdkafka/rdkafkacpp.h>


char hostname[128];
char errstr[512];

rd_kafka_conf_t *conf = rd_kafka_conf_new();

if (gethostname(hostname, sizeof(hostname))) {
 fprintf(stderr, "%% Failed to lookup hostname\n");
 exit(1);
}

if (rd_kafka_conf_set(conf, "client.id", hostname,
                     errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
 fprintf(stderr, "%% %s\n", errstr);
 exit(1);
}

if (rd_kafka_conf_set(conf, "group.id", "foo",
                     errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
 fprintf(stderr, "%% %s\n", errstr);
 exit(1);
}

if (rd_kafka_conf_set(conf, "bootstrap.servers", "host1:9092,host2:9092",
                     errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
 fprintf(stderr, "%% %s\n", errstr);
 exit(1);
}

/* Create Kafka consumer handle */
rd_kafka_t *rk;
if (!(rk = rd_kafka_new(RD_KAFKA_CONSUMER, conf,
                       errstr, sizeof(errstr)))) {
 fprintf(stderr, "%% Failed to create new consumer: %s\n", errstr);
 exit(1);
}

while (running) {
 rd_kafka_message_t *rkmessage = rd_kafka_consumer_poll(rk, 500);
 if (rkmessage) {
   msg_process(rkmessage);
   rd_kafka_message_destroy(rkmessage);

   if ((++msg_count % MIN_COMMIT_COUNT) == 0)
     rd_kafka_commit(rk, NULL, 0);
 }
}