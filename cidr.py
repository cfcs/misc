def match(cidr, ip):
  def ip_to_int(ip):
    octets = ip.split('.')
    return sum(int(octets[c//8]) << (24-c) for c in (0,8,16,24))
  (base, mask) = cidr.split('/')
  shift = 32 - int(mask)
  mask = (0xffffFFFF >> shift) << shift
  return ip_to_int(ip) & mask == ip_to_int(base) & mask

def test(cidr, ip):
  print('%s in %s: %s' % (ip, cidr, match(cidr, ip)))

test('1.2.3.4/32', '1.2.3.4')
test('1.2.3.4/32', '1.2.3.5')
test('1.2.3.4/31', '1.2.3.5')
test('1.2.3.0/24', '1.2.3.4')
test('1.2.3.0/24', '1.2.3.5')



# start \ exclude  (forall x, x E start /\ ~ (x E exclude) )
# from stackoverflow:
from ipaddress import ip_network
start = '0.0.0.0/0'
exclude = sys.argv[1:] or ['1.2.3.4/32']
result = [ip_network(start)]
for x in exclude:
  n = ip_network(x)
  new = []
  for y in result:
    if y.overlaps(n):
      new.extend(y.address_exclude(n))
    else:
      new.append(y)
  result = new
