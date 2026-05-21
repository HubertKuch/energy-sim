import grpc
from solar_solver.pb import solar_pb2
from solar_solver.pb import solar_pb2_grpc
from solar_solver.engine import solve_solar

class SolarSolverServicer(solar_pb2_grpc.SolarSolverServicer):
    def Solve(self, request, context):
        try:
            return solve_solar(request)
        except Exception as e:
            import traceback
            traceback.print_exc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return solar_pb2.SolarResponse()
