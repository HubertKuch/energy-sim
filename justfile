# Justfile for solar project

PROJECT_DIR := "solver"
GATEWAY_DIR := "gateway"
GO_BIN := "/bin/go"
PROTOC_GEN_GO := "/home/hubertkuch/Przestrzenie/Praca/go/bin/protoc-gen-go"
PROTOC_GEN_GO_GRPC := "/home/hubertkuch/Przestrzenie/Praca/go/bin/protoc-gen-go-grpc"

# Generate all gRPC code
generate: generate-python generate-go

# Generate gRPC Python code
generate-python:
    ~/.local/bin/uv --project {{PROJECT_DIR}} run python -m grpc_tools.protoc \
        -Iproto \
        --python_out={{PROJECT_DIR}}/solar_solver/pb \
        --grpc_python_out={{PROJECT_DIR}}/solar_solver/pb \
        proto/solar.proto
    # Fix imports in generated files to be relative within the package
    sed -i 's/import solar_pb2 as solar__pb2/from . import solar_pb2 as solar__pb2/' {{PROJECT_DIR}}/solar_solver/pb/solar_pb2_grpc.py

# Generate gRPC Go code
generate-go:
    mkdir -p {{GATEWAY_DIR}}/pb
    protoc -Iproto \
        --go_out={{GATEWAY_DIR}}/pb --go_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
        --go-grpc_out={{GATEWAY_DIR}}/pb --go-grpc_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
        --plugin=protoc-gen-go={{PROTOC_GEN_GO}} \
        --plugin=protoc-gen-go-grpc={{PROTOC_GEN_GO_GRPC}} \
        proto/solar.proto

# Run the solar solver server (Python)
run-solver: generate-python
    PYTHONPATH={{PROJECT_DIR}} ~/.local/bin/uv --project {{PROJECT_DIR}} run python {{PROJECT_DIR}}/main.py

# Run the gateway (Go)
run-gateway: generate-go
    cd {{GATEWAY_DIR}} && {{GO_BIN}} run main.go

# Run tests
test:
    PYTHONPATH={{PROJECT_DIR}} ~/.local/bin/uv --project {{PROJECT_DIR}} run pytest {{PROJECT_DIR}}/tests

# Run system integration test
system-test:
    PYTHONPATH=solver ~/.local/bin/uv --project solver run python tests/system_test.py
