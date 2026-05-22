package simulation

import (
	"time"

	pb "github.com/hubertkuch/solar/gateway/pb"
)

type SolarPanel struct {
	Pdc0          float64 `json:"pdc0"`
	Vmp           float64 `json:"v_mp"`
	Imp           float64 `json:"i_mp"`
	Voc           float64 `json:"v_oc"`
	Isc           float64 `json:"i_sc"`
	GammaPdc      float64 `json:"gamma_pdc"`
	AlphaSc       float64 `json:"alpha_sc"`
	BetaVoc       float64 `json:"beta_voc"`
	CellsInSeries int32   `json:"cells_in_series"`
}

type SolarInverter struct {
	Pdc0      float64 `json:"pdc0"`
	EtaInvNom float64 `json:"eta_inv_nom"`
	VdcMax    float64 `json:"v_dc_max"`
}

type SolarBattery struct {
	CapacityKwh   float64 `json:"capacity_kwh"`
	MaxChargeKw   float64 `json:"max_charge_kw"`
	MaxDischargeKw float64 `json:"max_discharge_kw"`
	Efficiency    float64 `json:"efficiency"`
	InitialSocKwh float64 `json:"initial_soc_kwh"`
}

type SimulationRequest struct {
	Location      *pb.Location  `json:"location"`
	SystemConfig  *SystemConfig `json:"system_config"`
	Date          string        `json:"date"` // Format: YYYY-MM-DD
	LoadProfileKw []float64     `json:"load_profile_kw"`
}

type SystemConfig struct {
	Arrays   []SolarArray  `json:"arrays"`
	Inverter *SolarInverter `json:"inverter"`
	Battery  *SolarBattery  `json:"battery"`
}

type SolarArray struct {
	SurfaceTilt      float64     `json:"surface_tilt"`
	SurfaceAzimuth   float64     `json:"surface_azimuth"`
	ModulesPerString int32       `json:"modules_per_string"`
	Strings          int32       `json:"strings"`
	Panel            *SolarPanel `json:"panel"`
}

type SimulationResponse struct {
	AcOutput       []float64 `json:"ac_output"`
	Timestamps     []string  `json:"timestamps"`
	BatterySocKwh  []float64 `json:"battery_soc_kwh"`
	GridImportKw   []float64 `json:"grid_import_kw"`
	GridExportKw   []float64 `json:"grid_export_kw"`
}

type SolveRequest struct {
	Arrays        []SolarArray   `json:"arrays"`
	Inverter      *SolarInverter `json:"inverter"`
	Battery       *SolarBattery  `json:"battery"`
	Duration      string         `json:"duration"` // e.g. "24h"
	When          string         `json:"when"`     // e.g. "2026-06-21T00:00:00Z"
	Temperature   float64        `json:"temperature"`
	Location      *pb.Location   `json:"location"`
	LoadProfileKw []float64      `json:"load_profile_kw"`
}

// Internal representation for the Solve call
type SolveParams struct {
	Arrays        []SolarArray
	Inverter      *SolarInverter
	Battery       *SolarBattery
	Duration      time.Duration
	When          time.Time
	Temperature   float64
	Location      *pb.Location
	LoadProfileKw []float64
}
