#!/bin/bash

if [ -n "$command" ]; then
  eval "$command"
else
  crunch42_scan json-report check-sqg $report_path
fi
