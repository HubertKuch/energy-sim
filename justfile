# Justfile for solar project

PROJECT_DIR := "solver"
GATEWAY_DIR := "gateway"

# Tool binaries (assumed to be in PATH, can be overridden)
GO := "go"
UV := "uv"
PROTOC := "protoc"

# Generate all gRPC code
generate: generate-python generate-go

# Generate gRPC Python code
generate-python:
	{{UV}} --project {{PROJECT_DIR}} run python -m grpc_tools.protoc \
		-Iproto \
		--python_out={{PROJECT_DIR}}/solar_solver/pb \
		--grpc_python_out={{PROJECT_DIR}}/solar_solver/pb \
		proto/solar.proto
	# Fix imports in generated files to be relative within the package
	sed -i 's/import solar_pb2 as solar__pb2/from . import solar_pb2 as solar__pb2/' {{PROJECT_DIR}}/solar_solver/pb/solar_pb2_grpc.py

# Generate gRPC Go code
generate-go:
	mkdir -p {{GATEWAY_DIR}}/pb
	{{PROTOC}} -Iproto \
		--go_out={{GATEWAY_DIR}}/pb --go_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
		--go-grpc_out={{GATEWAY_DIR}}/pb --go-grpc_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
		proto/solar.proto

# Run the solar solver server (Python)
run-solver: generate-python
	cd {{PROJECT_DIR}} && {{UV}} run python main.py

# Run the gateway (Go)
run-gateway: generate-go
	cd {{GATEWAY_DIR}} && {{GO}} run .

# Run all unit tests
test: test-python test-go

# Run Python unit tests
test-python:
	cd {{PROJECT_DIR}} && {{UV}} run pytest tests

# Run Go unit tests
test-go:
	cd {{GATEWAY_DIR}} && {{GO}} test -v ./...

# Run all integration tests
integration-test:
	cd {{PROJECT_DIR}} && {{UV}} run pytest ../tests/system_test.py ../tests/edge_cases_test.py ../tests/battery_test.py
