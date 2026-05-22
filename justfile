# Justfile for solar project

PROJECT_DIR := "solver"
GATEWAY_DIR := "gateway"

# Tool binaries
GO := "go"
UV := "uv"
PROTOC := "protoc"

# Generate all gRPC code
generate: generate-python generate-go

generate-python:
	{{UV}} --project {{PROJECT_DIR}} run python -m grpc_tools.protoc \
		-Iproto \
		--python_out={{PROJECT_DIR}}/solar_solver/pb \
		--grpc_python_out={{PROJECT_DIR}}/solar_solver/pb \
		proto/solar.proto
	sed -i 's/import solar_pb2 as solar__pb2/from . import solar_pb2 as solar__pb2/' {{PROJECT_DIR}}/solar_solver/pb/solar_pb2_grpc.py

generate-go:
	mkdir -p {{GATEWAY_DIR}}/pb
	{{PROTOC}} -Iproto \
		--go_out={{GATEWAY_DIR}}/pb --go_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
		--go-grpc_out={{GATEWAY_DIR}}/pb --go-grpc_opt=module=github.com/hubertkuch/solar/gateway/pb/solar \
		proto/solar.proto

test: test-solver test-gateway

test-solver:
	cd {{PROJECT_DIR}} && {{UV}} run pytest tests

test-gateway:
	cd {{GATEWAY_DIR}}/internal/simulation && {{GO}} test -v -coverprofile=coverage.out . && {{GO}} tool cover -func=coverage.out

cov-solver: test-solver
	cd {{PROJECT_DIR}} && xdg-open htmlcov/index.html || open htmlcov/index.html

cov-gateway: test-gateway
	cd {{GATEWAY_DIR}}/internal/simulation && {{GO}} tool cover -html=coverage.out

integration-test:
	cd {{PROJECT_DIR}} && {{UV}} run pytest ../tests/system_test.py ../tests/edge_cases_test.py ../tests/battery_test.py
