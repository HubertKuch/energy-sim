package uldk

import "fmt"

// ParcelRequest defines the parameters for a GetParcelByXY request.
type ParcelRequest struct {
	X    float64
	Y    float64
	SRID int
}

// ParcelResponse represents the parsed response from the ULDK service.
type ParcelResponse struct {
	ParcelID string
	WKB      string
}

// ULDKError represents a specialized error from the ULDK service.
type ULDKError struct {
	Code    int
	Message string
}

func (e *ULDKError) Error() string {
	return fmt.Sprintf("ULDK error: code %d, message: %s", e.Code, e.Message)
}
