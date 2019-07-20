import argparse
import datetime
from org.opentripplanner.scripting.api import OtpsEntryPoint
now = datetime.datetime.now()

# Define script arguments
parser = argparse.ArgumentParser()
parser.add_argument('--graph', default = '.') # path to graphs
parser.add_argument('--router', default = 'portland') 
parser.add_argument('--points', default = 'points.csv')
parser.add_argument('--dests')
parser.add_argument('--origins')
parser.add_argument('--date', nargs = 3, type = int, default = [2015, 9, 14]) # default = [now.year, now.month, now.day])
parser.add_argument('--time', nargs = 3, type = int, default = [10, 00, 00]) # default = [now.hour, now.minute, now.second])
parser.add_argument('--modes', default = 'WALK,BUS,RAIL')
parser.add_argument('--maxTimeSec', type = int, default = 7200)
parser.add_argument('--output_file', default = 'tt_matrix.csv')
parser.add_argument('--output_vars', nargs = '+',
    default = ['walk_distance', 'travel_time', 'boardings'])
args = parser.parse_args()

# Instantiate an OtpsEntryPoint
otp = OtpsEntryPoint.fromArgs(['--graphs', args.graph,
                               '--router', args.router])

# Start timing the code
import time
start_time = time.time()

# Get the default router
router = otp.getRouter('portland')

# Create a default request for a given departure time
req = otp.createRequest()
req.setDateTime(args.date[0], args.date[1], args.date[2],
    args.time[0], args.time[1], args.time[2])  # set departure time
req.setMaxTimeSec(args.maxTimeSec)  # set a limit to maximum travel time (seconds)
req.setModes(args.modes)    # define transport modes
# req.maxWalkDistance = 3000                 # set the maximum distance (in meters) the user is willing to walk
# req.walkSpeed = walkSpeed                 # set average walking speed ( meters ?)
# req.bikeSpeed = bikeSpeed                 # set average cycling speed (miles per hour ?)
# ?ERROR req.setSearchRadiusM(500)                 # set max snapping distance to connect trip origin to street network

# for more routing options, check: http://dev.opentripplanner.org/javadoc/0.19.0/org/opentripplanner/scripting/api/OtpsRoutingRequest.html

# Read Points of Destination - The file points.csv contains the columns GEOID, X and Y.
if args.origins is not None:
    origins = otp.loadCSVPopulation(args.origins, 'Y', 'X')
    dests = otp.loadCSVPopulation(args.dests, 'Y', 'X')
else:
    origins = otp.loadCSVPopulation(args.points, 'Y', 'X')
    dests = otp.loadCSVPopulation(args.points, 'Y', 'X')

# Create a CSV output
matrixCsv = otp.createCSVOutput()
matrixCsv.setHeader([ 'origin', 'destination'] + args.output_vars)

# Start Loop
for origin in origins:
  print('Processing origin:' + str(origin))
  req.setOrigin(origin)
  spt = router.plan(req)
  if spt is None: continue

  # Evaluate the SPT for all points
  result = spt.eval(dests)

  # Add a new row of result in the CSV output
  for r in result:
    # http://dev.opentripplanner.org/javadoc/0.19.0/index-all.html
    matrixCsv.addRow([ origin.getStringData('GEOID'),
        r.getIndividual().getStringData('GEOID'), # ] +
        # [r.getWalkDistance()] if 'walk_distance' in args.output_vars else [] +
        # [r.getTime()] if 'travel_time' in args.output_vars else [] +
        # [r.getBoardings()] if 'boardings' in args.output_vars else [])
        r.getWalkDistance(),
        r.getTime(),
        r.getBoardings()])
        # from other APIs
        # getTransferTime(Stop, Stop, Trip, Trip, boolean)
        # getFrequencyTripCount()
        # getFareAttribute()
        # getFare(Fare.FareType)
        # getDuration()
        # getDistance()
        # getCost(GraphPath)

# Save the result
matrixCsv.save(args.output_file)

# Stop timing the code
print("Elapsed time was %g seconds" % (time.time() - start_time))
