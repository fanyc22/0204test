import re
import json
import argparse
import subprocess
import itertools
import os

def killall():
	try:
		subprocess.check_output("killall ib_write_bw", shell=True)
	except Exception as e:
		pass
	try:
		subprocess.check_output("killall ib_read_bw", shell=True)
	except Exception as e:
		pass
	try:
		subprocess.check_output("killall ib_send_bw", shell=True)
	except Exception as e:
		pass
	try:
		subprocess.check_output("killall ib_atomic_bw", shell=True)
	except Exception as e:
		pass

def monitor_test(PCI:str,counters:list):
    cmd="ethtool -S {}".format(PCI)
    result=subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).decode("utf-8")
    counter_values={}
    for counter in counters:
        counter_values[counter]=re.search(r'{}:\s+(\d+)'.format(counter),result).group(1)
    return counter_values

#def show_regs(regs:str):

def run_test(config: dict, type: str):
    print("Running {}_{}.sh".format(config["exefile"], type))
    cmd = "bash {}_{}.sh".format(config["exefile"], type)
    for f1, f2, s1, s2, q1, q2, l1, l2, n1, n2 in itertools.product(config["f1"], config["f2"], config["s1"], config["s2"], config["q1"], config["q2"], config["l1"], config["l2"], config["n1"], config["n2"]):
        killall()
        arg = " -f1 {} -f2 {} -s1 {} -s2 {} -q1 {} -q2 {} -l1 {} -l2 {} -n1 {} -n2 {}".format(
            f1, f2, s1, s2, q1, q2, l1, l2, n1, n2)
        subprocess.run(cmd+arg, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Run Test")
    parser.add_argument("--config", type=str, default="config.json", help="Path to the config file")
    parser.add_argument("--type", type=str, default="all", help="Type to run the test.sh")
    args=parser.parse_args()
    config={}
    with open(args.config, "r") as config_file:
        config = json.load(config_file)
    if args.type=="all":
        run_test(config, "ww")
        run_test(config, "wr")
        run_test(config, "rr")
    else:
        run_test(config, args.type)

if __name__ == "__main__":
    main()