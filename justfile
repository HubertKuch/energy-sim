# Justfile for solar project

PROJECT_DIR := "solver"

# Generate gRPC Python code
generate:
    ~/.local/bin/uv --project {{PROJECT_DIR}} run python -m grpc_tools.protoc \
        -Iproto \
        --python_out={{PROJECT_DIR}}/solar_solver/pb \
        --grpc_python_out={{PROJECT_DIR}}/solar_solver/pb \
        proto/solar.proto
    # Fix imports in generated files to be relative within the package
    sed -i 's/import solar_pb2 as solar__pb2/from . import solar_pb2 as solar__pb2/' {{PROJECT_DIR}}/solar_solver/pb/solar_pb2_grpc.py

# Run the solar solver server
run: generate
    PYTHONPATH={{PROJECT_DIR}} ~/.local/bin/uv --project {{PROJECT_DIR}} run python {{PROJECT_DIR}}/main.py

# Run tests
test:
    PYTHONPATH={{PROJECT_DIR}} ~/.local/bin/uv --project {{PROJECT_DIR}} run pytest {{PROJECT_DIR}}/tests
