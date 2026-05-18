import grpc
from concurrent import futures
from solar_solver.pb import solar_pb2_grpc
from solar_solver.service import SolarSolverServicer

def serve(port="50051"):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    solar_pb2_grpc.add_SolarSolverServicer_to_server(SolarSolverServicer(), server)
    
    server.add_insecure_port(f'[::]:{port}')
    print(f"Solar Solver gRPC server starting on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
