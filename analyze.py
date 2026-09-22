# PC full analytics - real hardware numbers via psutil. Run: python analyze.py
import psutil, platform, datetime, socket

def gb(n):
    return round(n / (1024 ** 3), 2)

print('=== PC FULL ANALYTICS ===')
print('Computer:', socket.gethostname())
print('System:', platform.system(), platform.release(), platform.version())
print('Processor:', platform.processor() or platform.machine())
print('Boot time:', datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M'))

print('\n--- CPU ---')
print('Cores (physical/logical):', psutil.cpu_count(False), '/', psutil.cpu_count(True))
try:
    f = psutil.cpu_freq()
    print('Frequency now/max: %d / %d MHz' % (f.current, f.max))
except Exception as e:
    print('Frequency: n/a', e)
print('Usage overall (1s sample):', psutil.cpu_percent(interval=1), '%')
print('Usage per core:', psutil.cpu_percent(interval=1, percpu=True))

print('\n--- MEMORY ---')
m = psutil.virtual_memory()
print('RAM total/used/free: %s / %s / %s GB (%s%% used)' % (gb(m.total), gb(m.used), gb(m.free), m.percent))
s = psutil.swap_memory()
print('Swap total/used: %s / %s GB' % (gb(s.total), gb(s.used)))

print('\n--- DISKS ---')
for p in psutil.disk_partitions():
    try:
        u = psutil.disk_usage(p.mountpoint)
        print('%s (%s): %s / %s GB used (%s%%) - %s' % (p.device, p.fstype, gb(u.used), gb(u.total), u.percent, p.mountpoint))
    except PermissionError:
        print(p.device, ': access denied')
io = psutil.disk_io_counters()
print('Disk read/written total: %s / %s GB' % (gb(io.read_bytes), gb(io.write_bytes)))

print('\n--- NETWORK ---')
for name, addrs in psutil.net_if_addrs().items():
    ips = [a.address for a in addrs if a.family == socket.AF_INET]
    if ips:
        print(name, '->', ', '.join(ips))
nio = psutil.net_io_counters()
print('Net sent/received total: %s / %s GB' % (gb(nio.bytes_sent), gb(nio.bytes_recv)))

print('\n--- BATTERY ---')
b = psutil.sensors_battery()
print('Battery:', (str(round(b.percent)) + '% ' + ('charging' if b.power_plugged else 'on battery')) if b else 'no battery (desktop)')

print('\n--- TOP 5 PROCESSES BY CPU ---')
procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
               key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:5]
for p in procs:
    print('%-25s pid=%-6s cpu=%s%% mem=%s%%' % (str(p.info['name'])[:25], p.info['pid'], p.info['cpu_percent'], round(p.info['memory_percent'] or 0, 1)))

print('\n--- TOP 5 PROCESSES BY RAM ---')
procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
               key=lambda p: p.info['memory_percent'] or 0, reverse=True)[:5]
for p in procs:
    print('%-25s pid=%-6s mem=%s%% cpu=%s%%' % (str(p.info['name'])[:25], p.info['pid'], round(p.info['memory_percent'] or 0, 1), p.info['cpu_percent']))

print('\n=== DONE ===')
