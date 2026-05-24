package simulation

import (
	"context"
	"fmt"
	"time"

	"github.com/hubertkuch/solar/gateway/internal/weather"
	pb "github.com/hubertkuch/solar/gateway/pb"
)

// SimulationService defines the business logic operations for simulations.
type SimulationService interface {
	RunSimulation(ctx context.Context, req *SimulationRequest) (*SimulationResponse, error)
	Solve(ctx context.Context, params SolveParams, weatherData []*pb.WeatherData) (*SimulationResponse, error)
	GetWeather(ctx context.Context, params SolveParams) ([]*pb.WeatherData, error)
}

// simulationService implements SimulationService using a gRPC client.
type simulationService struct {
	client          pb.SolarSolverClient
	weatherProvider weather.Provider
}

// NewSimulationService creates a new SimulationService.
func NewSimulationService(client pb.SolarSolverClient, weatherProvider weather.Provider) SimulationService {
	return &simulationService{
		client:          client,
		weatherProvider: weatherProvider,
	}
}

// Solve executes the gRPC call to the Python solver using "ready" weather data.
func (s *simulationService) Solve(ctx context.Context, params SolveParams, weatherData []*pb.WeatherData) (*SimulationResponse, error) {
	pbArrays := s.mapArraysToProto(params.Arrays)

	solarReq := &pb.SolarRequest{
		Location: params.Location,
		SystemConfig: &pb.SystemConfig{
			Arrays: pbArrays,
			Inverter: &pb.SolarInverter{
				Pdc0:      params.Inverter.Pdc0,
				EtaInvNom: params.Inverter.EtaInvNom,
				VDcMax:    params.Inverter.VdcMax,
			},
		},
		Weather:       weatherData,
		LoadProfileKw: params.LoadProfileKw,
	}

	if params.Battery != nil {
		solarReq.SystemConfig.Battery = &pb.SolarBattery{
			CapacityKwh:    params.Battery.CapacityKwh,
			MaxChargeKw:    params.Battery.MaxChargeKw,
			MaxDischargeKw: params.Battery.MaxDischargeKw,
			Efficiency:     params.Battery.Efficiency,
			InitialSocKwh:  params.Battery.InitialSocKwh,
		}
	}

	res, err := s.client.Solve(ctx, solarReq)
	if err != nil {
		return nil, fmt.Errorf("gRPC call failed: %w", err)
	}

	return &SimulationResponse{
		AcOutput:      res.AcOutput,
		Timestamps:    res.Timestamps,
		BatterySocKwh: res.BatterySocKwh,
		GridImportKw:  res.GridImportKw,
		GridExportKw:  res.GridExportKw,
	}, nil
}

// RunSimulation is a legacy wrapper for daily simulations.
func (s *simulationService) RunSimulation(ctx context.Context, req *SimulationRequest) (*SimulationResponse, error) {
	date, err := time.Parse("2006-01-02", req.Date)
	if err != nil {
		return nil, fmt.Errorf("invalid date format: %w", err)
	}

	params := SolveParams{
		Arrays:        req.SystemConfig.Arrays,
		Inverter:      req.SystemConfig.Inverter,
		Battery:       req.SystemConfig.Battery,
		Duration:      24 * time.Hour,
		When:          date,
		Temperature:   20.0,
		SnowDepthCm:   req.SnowDepthCm,
		Location:      req.Location,
		LoadProfileKw: req.LoadProfileKw,
	}

	weatherData, err := s.GetWeather(ctx, params)
	if err != nil {
		return nil, err
	}

	return s.Solve(ctx, params, weatherData)
}

func (s *simulationService) mapArraysToProto(arrays []SolarArray) []*pb.SolarArray {
	var pbArrays []*pb.SolarArray
	for _, arr := range arrays {
		pbArrays = append(pbArrays, &pb.SolarArray{
			SurfaceTilt:      arr.SurfaceTilt,
			SurfaceAzimuth:   arr.SurfaceAzimuth,
			ModulesPerString: arr.ModulesPerString,
			Strings:          arr.Strings,
			Panel: &pb.SolarPanel{
				Pdc0:          arr.Panel.Pdc0,
				VMp:           arr.Panel.Vmp,
				IMp:           arr.Panel.Imp,
				VOc:           arr.Panel.Voc,
				ISc:           arr.Panel.Isc,
				GammaPdc:      arr.Panel.GammaPdc,
				AlphaSc:       arr.Panel.AlphaSc,
				BetaVoc:       arr.Panel.BetaVoc,
				CellsInSeries: arr.Panel.CellsInSeries,
			},
		})
	}
	return pbArrays
}
