"""Machine sampler. Compressor, swap used, swap free, page-outs. Never free."""
import re, subprocess
def sample():
    vm = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    ps = int(re.search(r"page size of (\d+)", vm).group(1))
    def g(k):
        m = re.search(rf"{re.escape(k)}:\s+(\d+)", vm)
        return int(m.group(1)) if m else 0
    sw = subprocess.run(["sysctl","-n","vm.swapusage"],capture_output=True,text=True).stdout
    used = float(re.search(r"used = ([\d.]+)M", sw).group(1))
    free = float(re.search(r"free = ([\d.]+)M", sw).group(1))
    tot  = float(re.search(r"total = ([\d.]+)M", sw).group(1))
    return {"compressor_gib": round(g("Pages occupied by compressor")*ps/2**30, 3),
            "swap_used_mb": used, "swap_free_mb": free, "swap_total_mb": tot,
            "pageouts_cumulative": g("Pageouts"),
            "compressions_cumulative": g("Compressions")}
if __name__ == "__main__":
    s = sample()
    for k, v in s.items():
        print(f"  {k:<26} {v}")
