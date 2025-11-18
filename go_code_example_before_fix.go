package main

import (
	"encoding/json"
	"fmt"
)

type AssociateAccessPolicyInput struct {
	PolicyArn string `json:"policyArn"`
	TargetId  string `json:"targetId"`
}

func handleRequest(jsonData []byte) error {
	// 문제가 되는 코드: input 변수가 초기화되지 않음
	var input *AssociateAccessPolicyInput

	// input이 nil이므로 json.Unmarshal은 패닉을 발생시킴
	err := json.Unmarshal(jsonData, input)
	if err != nil {
		return err
	}

	fmt.Printf("Policy: %s, Target: %s\n", input.PolicyArn, input.TargetId)
	return nil
}
