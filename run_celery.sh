#!/bin/sh
# Wait for broker
sleep 10
# Run celery
celery worker -A vera -B -l info
