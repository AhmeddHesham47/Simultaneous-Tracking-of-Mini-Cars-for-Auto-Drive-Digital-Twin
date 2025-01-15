using System;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;

public class carMovement1 : MonoBehaviour
{
    // UDP receiver for getting car data
    public UDPReceive udpReceive;

    // GameObjects representing the cars in Unity
    public GameObject Car_1;
    public GameObject Car_2;
    public GameObject Car_3;
    public GameObject Car_4;

    // Fixed Y position for stability
    public float stableY = 0f;

    // Smoothing factor for movement
    public float smoothing = 7f;

    // Maximum allowed position change per update
    public float maxPositionDelta = 0.7f;

    // Dictionaries to store previous positions, rotations, and buffered car data
    private Dictionary<int, Vector3> previousPositions;
    private Dictionary<int, Quaternion> previousRotations;
    private Dictionary<int, CarData> carDataBuffer;

    // Struct to store car data
    private struct CarData
    {
        public Vector3 position;
        public Quaternion rotation;
        public float timestamp;
    }

    void Awake()
    {
        // Initialize dictionaries
        previousPositions = new Dictionary<int, Vector3>();
        previousRotations = new Dictionary<int, Quaternion>();
        carDataBuffer = new Dictionary<int, CarData>();

        // Initialize car data for all tracked cars
        InitializeCarData(1, Car_1);
        InitializeCarData(2, Car_2);
        InitializeCarData(3, Car_3);
        InitializeCarData(4, Car_4);
    }

    private void InitializeCarData(int id, GameObject car)
    {
        if (car != null)
        {
            // Store initial positions and rotations
            previousPositions[id] = car.transform.localPosition;
            previousRotations[id] = car.transform.localRotation;

            // Initialize car data buffer with current state
            carDataBuffer[id] = new CarData
            {
                position = car.transform.localPosition,
                rotation = car.transform.localRotation,
                timestamp = Time.time
            };
        }
    }

    void Update()
    {
        // Process received UDP data
        ProcessUDPData();

        // Update car positions based on latest data
        UpdateCarPositions();
    }

    private void ProcessUDPData()
    {
        // Retrieve the latest UDP data
        string[] dataLines = udpReceive.GetLatestData();
        if (dataLines == null) return;

        foreach (string data in dataLines)
        {
            if (string.IsNullOrEmpty(data)) continue;

            try
            {
                // Split incoming data string into components
                string[] info = data.Split(',');
                if (info.Length >= 4)
                {
                    int id = int.Parse(info[0].Trim()); // Car ID
                    float x = 8 + float.Parse(info[1].Trim()) / 75; // Convert X position
                    float z = float.Parse(info[2].Trim()) / 75; // Convert Z position
                    float rotationY = float.Parse(info[3].Trim()); // Yaw rotation
                    rotationY += 360; // Normalize rotation

                    // Validate car ID and update buffer
                    if (IsValidCarId(id))
                    {
                        CarData carData = new CarData
                        {
                            position = new Vector3(x, stableY, z),
                            rotation = Quaternion.Euler(0, rotationY, 0),
                            timestamp = Time.time
                        };

                        carDataBuffer[id] = carData;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"Error processing data line: {data}\nError: {e.Message}");
            }
        }
    }

    private bool IsValidCarId(int id)
    {
        // Ensure the car ID is within the valid range
        return id == 1 || id == 2 || id == 3 || id == 4;
    }

    private void UpdateCarPositions()
    {
        float currentTime = Time.time;

        // Update each car based on the latest data
        if (Car_1 != null) UpdateCar(1, Car_1, currentTime);
        if (Car_2 != null) UpdateCar(2, Car_2, currentTime);
        if (Car_3 != null) UpdateCar(3, Car_3, currentTime);
        if (Car_4 != null) UpdateCar(4, Car_4, currentTime);
    }

    private void UpdateCar(int id, GameObject car, float currentTime)
    {
        // Ensure data exists for this car
        if (!carDataBuffer.ContainsKey(id) || !previousPositions.ContainsKey(id) || !previousRotations.ContainsKey(id))
        {
            return; // Skip if data is incomplete
        }

        var carData = carDataBuffer[id];
        if (currentTime - carData.timestamp > 1f)
        {
            return; // Skip outdated data
        }

        Vector3 prevPosition = previousPositions[id];
        Quaternion prevRotation = previousRotations[id];

        // Smooth position transition and apply position delta constraint
        Vector3 smoothedPosition = Vector3.Lerp(prevPosition, carData.position, smoothing * Time.deltaTime);
        smoothedPosition = Vector3.MoveTowards(prevPosition, smoothedPosition, maxPositionDelta);

        // Smooth rotation transition
        Quaternion smoothedRotation = Quaternion.Lerp(prevRotation, carData.rotation, smoothing * Time.deltaTime);

        // Apply updated transformations to the car
        car.transform.localPosition = smoothedPosition;
        car.transform.localRotation = smoothedRotation;

        // Store updated positions and rotations for next frame
        previousPositions[id] = smoothedPosition;
        previousRotations[id] = smoothedRotation;
    }
}
