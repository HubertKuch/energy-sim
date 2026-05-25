package uldk

import (
	"context"
	"fmt"
	"strings"
)

// GetParcelGeomByCoordinates fetches parcel geometry and ID for given coordinates.
// It uses the GetParcelByXY request.
func (c *Client) GetParcelGeomByCoordinates(ctx context.Context, req ParcelRequest) (*ParcelResponse, error) {
	srid := req.SRID
	if srid == 0 {
		srid = 2180
	}

	url := fmt.Sprintf("%s?request=GetParcelByXY&xy=%f,%f&srid=%d&result=id,geom_wkb",
		c.baseURL, req.X, req.Y, srid)

	body, err := c.do(ctx, url)
	if err != nil {
		return nil, err
	}
	defer body.Close()

	dataLine, err := c.parseResponse(body)
	if err != nil {
		if strings.Contains(err.Error(), "no results found") {
			return nil, fmt.Errorf("no parcel found at coordinates %f, %f", req.X, req.Y)
		}
		return nil, err
	}

	if dataLine == "" {
		return nil, fmt.Errorf("missing data in uldk response")
	}

	parts := strings.Split(dataLine, "|")
	if len(parts) < 2 {
		return &ParcelResponse{
			WKB: dataLine,
		}, nil
	}

	return &ParcelResponse{
		ParcelID: parts[0],
		WKB:      parts[1],
	}, nil
}
