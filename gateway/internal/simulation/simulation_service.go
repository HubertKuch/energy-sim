package simulation

import (
	"context"
	"fmt"
	"math"
	"time"

	pb "github.com/hubertkuch/solar/gateway/pb"
)

// SimulationService defines the business logic operations for simulations.
type SimulationService interface {
	RunSimulation(ctx context.Context, req *SimulationRequest) (*SimulationResponse, error)
	Solve(ctx context.Context, params SolveParams) (*SimulationResponse, error)
}

// simulationService implements SimulationService using a gRPC client.
type simulationService struct {
	client pb.SolarSolverClient
}

// NewSimulationService creates a new SimulationService.
func NewSimulationService(client pb.SolarSolverClient) SimulationService {
	return &simulationService{
		client: client,
	}
}

func (s *simulationService) Solve(ctx context.Context, params SolveParams) (*SimulationResponse, error) {
	// Generate weather data based on duration and temperature
	var weatherData []*pb.WeatherData
	startTime := params.When
	hours := int(params.Duration.Hours())
	if hours == 0 {
		hours = 1
	}

	for h := 0; h < hours; h++ {
		ts := startTime.Add(time.Duration(h) * time.Hour)

		ghi := 0.0
		hourFloat := float64(ts.Hour())
		if hourFloat >= 6 && hourFloat <= 18 {
			ghi = 1000 * math.Exp(-math.Pow(hourFloat-12, 2)/16)
		}

		weatherData = append(weatherData, &pb.WeatherData{
			Timestamp:   ts.Format("2006-01-02 15:04:05"),
			Ghi:         ghi,
			Dni:         ghi * 0.8,
			Dhi:         ghi * 0.2,
			TempAir:     params.Temperature,
			WindSpeed:   2,
			SnowDepthCm: params.SnowDepthCm,
		})
	}

	// Map internal types to protobuf
	var pbArrays []*pb.SolarArray
	for _, arr := range params.Arrays {
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
		AcOutput:       res.AcOutput,
		Timestamps:     res.Timestamps,
		BatterySocKwh:  res.BatterySocKwh,
		GridImportKw:   res.GridImportKw,
		GridExportKw:   res.GridExportKw,
	}, nil
}

func (s *simulationService) RunSimulation(ctx context.Context, req *SimulationRequest) (*SimulationResponse, error) {
	// Parse date
	date, err := time.Parse("2006-01-02", req.Date)
	if err != nil {
		return nil, fmt.Errorf("invalid date format: %w", err)
	}

	weatherData := s.generateHourlyWeatherData(date, req.SnowDepthCm)

	// Map internal types to protobuf
	var pbArrays []*pb.SolarArray
	for _, arr := range req.SystemConfig.Arrays {
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

	solarReq := &pb.SolarRequest{
		Location: req.Location,
		SystemConfig: &pb.SystemConfig{
			Arrays: pbArrays,
			Inverter: &pb.SolarInverter{
				Pdc0:      req.SystemConfig.Inverter.Pdc0,
				EtaInvNom: req.SystemConfig.Inverter.EtaInvNom,
				VDcMax:    req.SystemConfig.Inverter.VdcMax,
			},
		},
		Weather:       weatherData,
		LoadProfileKw: req.LoadProfileKw,
	}

	if req.SystemConfig.Battery != nil {
		solarReq.SystemConfig.Battery = &pb.SolarBattery{
			CapacityKwh:   req.SystemConfig.Battery.CapacityKwh,
			MaxChargeKw:   req.SystemConfig.Battery.MaxChargeKw,
			MaxDischargeKw: req.SystemConfig.Battery.MaxDischargeKw,
			Efficiency:    req.SystemConfig.Battery.Efficiency,
			InitialSocKwh: req.SystemConfig.Battery.InitialSocKwh,
		}
	}

	res, err := s.client.Solve(ctx, solarReq)
	if err != nil {
		return nil, fmt.Errorf("gRPC call failed: %w", err)
	}

	return &SimulationResponse{
		AcOutput:       res.AcOutput,
		Timestamps:     res.Timestamps,
		BatterySocKwh:  res.BatterySocKwh,
		GridImportKw:   res.GridImportKw,
		GridExportKw:   res.GridExportKw,
	}, nil
}

func (s *simulationService) generateHourlyWeatherData(date time.Time, snowDepthCm float64) []*pb.WeatherData {
	var weatherData []*pb.WeatherData
	for h := 0; h < 24; h++ {
		ts := time.Date(date.Year(), date.Month(), date.Day(), h, 0, 0, 0, date.Location())

		ghi := 0.0
		hourFloat := float64(h)
		if h >= 6 && h <= 18 {
			ghi = 1000 * math.Exp(-math.Pow(hourFloat-12, 2)/16)
		}

		weatherData = append(weatherData, &pb.WeatherData{
			Timestamp:   ts.Format("2006-01-02 15:04:05"),
			Ghi:         ghi,
			Dni:         ghi * 0.8,
			Dhi:         ghi * 0.2,
			TempAir:     20,
			WindSpeed:   2,
			SnowDepthCm: snowDepthCm,
		})
	}
	return weatherData
}
