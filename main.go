package main

import (
	"fmt" 
	"io/ioutil"
	"log"
	"strings"
	"math"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/canvas" 
)
var currentMousePosition = [...]float32{0.0, 0.0}

const (
    EARTH_RADIUS  float32 = 6378137.0
    MAX_LATITUDE  float32 = 85.0511287798
)
const (
    MIN_MERCATOR_X float32 = -20037508.34
    MIN_MERCATOR_Y float32 = -20037508.34
    MAX_MERCATOR_X float32 = 20037508.34
    MAX_MERCATOR_Y float32 = 20037508.34
)

func degrees(radians float32) float32 {
	return radians * (180 / math.Pi)
}

func radians(degrees float32) float32 {
	return degrees * (math.Pi / 180)
}


func max(a, b float64) float64 {
    if a > b {
        return a
    }
    return b
}

func min(a, b float64) float64 {
    if a < b {
        return a
    }
    return b
}

func lerp(v float32 , from_min float32, from_max float32, to_min float32, to_max float32) float32 {
	return (v - from_min) / (from_max - from_min) * (to_max - to_min) + to_min
}

func webMercatorToLatLon(x float32, y float32) (float32, float32) {
    lon := degrees(float32(x) / float32(EARTH_RADIUS))
    lat := degrees(float32(2 * math.Atan(math.Exp(float64(y)/float64(EARTH_RADIUS))) - math.Pi/2))
    return float32(lat), float32(lon)
}

func latlonToWebMercator(lat float32, lon float32) (float32, float32) {
    lat = float32(max(float64(min(float64(MAX_LATITUDE), float64(lat))), float64(-MAX_LATITUDE)))
    x := float32(EARTH_RADIUS) * radians(float32(lon))
    y := float32(EARTH_RADIUS) * float32(math.Log(math.Tan(math.Pi/4 + float64(radians(lat))/2)))
    return x, y
}



func index(array []int, target int) int {
	for i, val := range array {
		if val == target {
			return i
		}
	}
	return -1 
}

func getMapFileList(dir string ) []string {
	files, err := ioutil.ReadDir(dir)
	imagepaths := []string{} 
	if err != nil {
		log.Fatal(err)
	}
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".png") {
			imagepaths = append(imagepaths, dir + "/" + file.Name())
		} 
	}
	return imagepaths
}

func getMap(scale int, dir string) *canvas.Image {
	avaibable_scales := []int{4096, 8192, 16384, 32768}

	imagepaths := getMapFileList(dir)
	currentScaleIndex := index(avaibable_scales, scale)

	mapToLoadFilepath := imagepaths[currentScaleIndex]
	img := canvas.NewImageFromFile(mapToLoadFilepath)
	return img
}

type hoverableImage struct {
	widget.BaseWidget
	image *canvas.Image
}


func newHoverableImage(img *canvas.Image) *hoverableImage {
	hi := &hoverableImage{image: img}
	hi.ExtendBaseWidget(hi)
	return hi
}

func (hi *hoverableImage) CreateRenderer() fyne.WidgetRenderer {
	return widget.NewSimpleRenderer(hi.image)
}

func (hi *hoverableImage) Cursor() desktop.Cursor {
	return desktop.DefaultCursor
}

func (hi *hoverableImage) MouseMoved(me *desktop.MouseEvent) {
	currentMousePosition[0] = me.Position.X
	currentMousePosition[1] = me.Position.Y
}


func (hi *hoverableImage) MouseIn(*desktop.MouseEvent) {
	// This method is called when the mouse enters the image area
}


func (hi *hoverableImage) MouseOut() {
	// This method is called when the mouse leaves the image area
}


type ZoomableImage struct {
	widget.BaseWidget 
	image *canvas.Image
	zoomFactor float64
}

func NewZoomableImage(img *canvas.Image) *ZoomableImage {
	zi := &ZoomableImage{image: img, zoomFactor: 1.0}
	zi.ExtendBaseWidget(zi)
	return zi 
}

func (zi *ZoomableImage) CreateRenderer() fyne.WidgetRenderer {
	return widget.NewSimpleRenderer(zi.image)
}

func (zi *ZoomableImage) SetZoomFactor(factor float64) {
	zi.zoomFactor = factor 
	zi.Refresh() 
}

func (zi *ZoomableImage) Tapped(ev *fyne.PointEvent) {
	zi.zoomFactor *= 1.2
	zi.Refresh()
}


func main() {
	fmt.Println("running")
	app := app.New()
	window := app.NewWindow("map")

	dir := "./map_resource"
	scale := 4096
	mapImage := getMap(scale, dir)
	
	hoverableMapImage := newHoverableImage(mapImage)
	// zoomableImg := NewZoomableImage(mapImage)
	

	scrollContainer := container.NewScroll(hoverableMapImage)
	window.SetContent(scrollContainer)


	window.Canvas().SetOnTypedKey(func(ke *fyne.KeyEvent) {
		if ke.Name == "P" {

			fmt.Println("mouse pos: ", currentMousePosition)
			posx, posy := float32(currentMousePosition[0] / float32(800.0) * float32(scale)), float32(currentMousePosition[1]/ float32(800.0) * float32(scale))
			
			mercatorMousePosition :=  [2]float32 {float32(0.0), float32(0.0)}
			mercatorMousePosition[0] = lerp(posx, 0, float32(scale), MIN_MERCATOR_X, MAX_MERCATOR_X)
			
			mercatorMousePosition[1] = lerp(posy, 0, float32(scale), MIN_MERCATOR_Y, MAX_MERCATOR_Y)

			lat, lon := webMercatorToLatLon(mercatorMousePosition[0], mercatorMousePosition[1])

			fmt.Println("m", lat, lon)
		}
	})

	window.Resize(fyne.NewSize(800, 800))
	window.ShowAndRun()
}