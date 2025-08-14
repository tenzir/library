#!/usr/bin/python3

import argparse
import re


# This script takes the CSV format defined in the headers on e.g.
# https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-admin/monitoring/use-syslog-for-monitoring/syslog-field-descriptions/traffic-log-fields#idbe18d2d4-9eb8-4966-bec8-df3a6de70e66
# and turns them into a CSV header string that Tenzir can use in `parse_csv`
def main():
  parser = argparse.ArgumentParser(description="Transform Palo Alto header list to Tenzir CSV Header")
  parser.add_argument("input_string", type=str, help="Input string to transform.")
  args = parser.parse_args()


  s = args.input_string.lower()
  s = s.replace("format: ","")
  s = s.replace(", ",",")
  s = s.replace(" ", "_")
  s = s.replace("-", "_")
  s = s.replace("/","_")

  # Replace 'future_use' with 'future_use1', 'future_use2', ...
  def future_use_replacer():
    count = 0
    def repl(match):
      nonlocal count
      count += 1
      return f"future_use{count}"
    return repl

  s = re.sub(r"future_use", future_use_replacer(), s)
  print(s)

if __name__ == "__main__" :
  main()
