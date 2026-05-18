import grpc
from solar_solver.pb import solar_pb2
from solar_solver.pb import solar_pb2_grpc
from solar_solver.engine import solve_solar

class SolarSolverServicer(solar_pb2_grpc.SolarSolverServicer):
    def Solve(self, request, context):
        try:
            ac_results = solve_solar(request)

            return solar_pb2.SolarResponse(
                ac_output=ac_results.tolist(),
                timestamps=[str(ts) for ts in ac_results.index]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return solar_pb2.SolarResponse()
