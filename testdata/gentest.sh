#!/bin/bash
head -c 1M </dev/urandom > 1M.blob
head -c 10M </dev/urandom > 10M.blob
head -c 100M </dev/urandom > 100M.blob
head -c 1G </dev/urandom > 1G.blob