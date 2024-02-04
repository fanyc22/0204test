import re
import json
import argparse
import subprocess
import itertools
import time


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


def monitor_test(PCI: str, counters: list):
    cmd = "ethtool -S {}".format(PCI)
    result = subprocess.run(
    	cmd, shell=True, stdout=subprocess.PIPE).decode("utf-8")
    counter_values = {}
    for counter in counters:
        counter_values[counter] = int(re.search(
            r'{}:\s+(\d+)'.format(counter), result).group(1))
    return counter_values

# def show_regs(NIC:str,regs:str):


def run_test(config: dict, type: str):
    print("Running {}_{}.sh".format(config["exefile"], type))
    cmd = "bash {}_{}.sh".format(config["exefile"], type)
    counters_A = [  # "rx_vport_rdma_unicast_packets",
        # "rx_vport_rdma_unicast_bytes",
        # "tx_vport_rdma_unicast_packets",
        # "tx_vport_rdma_unicast_bytes",
        # "rx_prio{}_bytes".format(config["hostA"]["priority"]),
        # "rx_prio{}_packets".format(config["hostA"]["priority"]),
        "tx_prio{}_bytes".format(config["hostA"]["priority"]),
        "tx_prio{}_packets".format(config["hostA"]["priority"])
    ]
    counters_B = [  # "rx_vport_rdma_unicast_packets",
        # "rx_vport_rdma_unicast_bytes",
        # "tx_vport_rdma_unicast_packets",
        # "tx_vport_rdma_unicast_bytes",
        "rx_prio{}_bytes".format(config["hostB"]["priority"]),
        "rx_prio{}_packets".format(config["hostB"]["priority"]),
        # "tx_prio{}_bytes".format(config["hostB"]["priority"]),
        # "tx_prio{}_packets".format(config["hostB"]["priority"])
    ]
    for f1, f2, s1, s2, q1, q2, l1, l2, n1, n2 in itertools.product(config["f1"], config["f2"], config["s1"], config["s2"], config["q1"], config["q2"], config["l1"], config["l2"], config["n1"], config["n2"]):
        killall()
        arg = " -f1 {} -f2 {} -s1 {} -s2 {} -q1 {} -q2 {} -l1 {} -l2 {} -n1 {} -n2 {}".format(
            f1, f2, s1, s2, q1, q2, l1, l2, n1, n2)
        subprocess.run(cmd+arg, shell=True)
        print("Test for {}".format(cmd+arg))
       
       #value_A
        old_time = time.time_ns()
        value_A_old = monitor_test(config["hostA"]["PCI"], counters_A)
        time.sleep(config["sleep"])
        new_time = time.time_ns()
        value_A_new = monitor_test(config["hostA"]["PCI"], counters_A)
        value_A={}
        value_A["bps"]=8*(value_A_new["tx_prio{}_bytes".format(config["hostA"]["priority"])]-value_A_old["tx_prio{}_bytes".format(config["hostA"]["priority"])])/(new_time-old_time)
        value_A["pps"]=(value_A_new["tx_prio{}_packets".format(config["hostA"]["priority"])]-value_A_old["tx_prio{}_packets".format(config["hostA"]["priority"])])/(new_time-old_time)
        
        #value_B
        old_time = time.time_ns()
        value_B_old = monitor_test(config["hostB"]["PCI"], counters_B)
        time.sleep(config["sleep"])
        new_time = time.time_ns()
        value_B_new = monitor_test(config["hostB"]["PCI"], counters_B)
        value_B={}
        value_B["bps"]=8*(value_B_new["rx_prio{}_bytes".format(config["hostB"]["priority"])]-value_B_old["rx_prio{}_bytes".format(config["hostB"]["priority"])])/(new_time-old_time)
        value_B["pps"]=(value_B_new["rx_prio{}_packets".format(config["hostB"]["priority"])]-value_B_old["rx_prio{}_packets".format(config["hostB"]["priority"])])/(new_time-old_time)

        print("HostA: bps: {} pps: {}".format(value_A["bps"], value_A["pps"]))
        print("HostB: bps: {} pps: {}".format(value_B["bps"], value_B["pps"]))

        # todo: regs
        # show_regs(config["hostA"]["NIC"],config["regs"])
        # show_regs(config["hostB"]["NIC"],config["regs"])
    
    print("Test for {} done".format(cmd))

def main():
    parser = argparse.ArgumentParser(description="Run Test")
    parser.add_argument("--config", type=str,
                        default="config.json", help="Path to the config file")
    parser.add_argument("--type", type=str, default="all",
                        help="Type to run the test.sh")
    args = parser.parse_args()
    config = {}
    with open(args.config, "r") as config_file:
        config = json.load(config_file)
    if args.type == "all":
        run_test(config, "ww")
        run_test(config, "wr")
        run_test(config, "rr")
    else:
        run_test(config, args.type)


if __name__ == "__main__":
    main()
