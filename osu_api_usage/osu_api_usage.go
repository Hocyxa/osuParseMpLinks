package osuParseMpLinks

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type secretData struct {
	Client_id     string
	Client_secret string
}

func (data secretData) getClientId() string {
	return data.Client_id
}
func (data secretData) getClientSecret() string {
	return data.Client_secret
}
func NewSecretData() secretData {

	jsonFile, err := os.Open("osu_api_usage/secrets.json")
	if err != nil {
		panic(err)
	}
	defer jsonFile.Close()

	byteValue, _ := io.ReadAll(jsonFile)
	var data *secretData
	json.Unmarshal(byteValue, &data)

	return secretData{
		data.getClientId(),
		data.getClientSecret(),
	}
}

type HttpClient struct {
	MgAPIKey string
	Client   *http.Client
}

func NewHttpClient(apikey string) HttpClient {
	return HttpClient{
		apikey,
		http.DefaultClient,
	}
}

func GetToken() {
	secret_data := NewSecretData()

	url := "https://osu.ppy.sh/oauth/token"

	req, err := http.NewRequest("POST", url, nil)
	if err != nil {
		panic(err)
	}
	q := req.URL.Query()
	q.Add("client_id", secret_data.getClientId())
	q.Add("client_secret", secret_data.getClientSecret())
	req.URL.RawQuery = q.Encode()
	//TODO найти как поменять шапку и отослать запрос с проверкой токена
	fmt.Println(req.URL.String())
}

func Get_user_data_by_username_or_id() {
	print("get_user_data_by_username_or_id")
}
