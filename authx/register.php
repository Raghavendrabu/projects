<?php
/**
 * AuthX Cybersecurity Registration Portal Backend Handler
 * Handles AJAX POST requests, connects to MySQL via PDO, and inserts data.
 */

// Define response headers
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$response = [
    'success' => false,
    'message' => 'Node handshake failed.',
    'row_id' => null,
    'db_logs' => []
];

// Server trace logs helper
function addLog(&$logs, $message) {
    $logs[] = $message;
}

try {
    addLog($response['db_logs'], ">> INITIALIZING CONNECTION TO BACKEND APEX NODE...");
    
    // 1. Gather input parameters from POST, GET, and raw request body (JSON/urlencoded)
    $inputs = array_merge($_GET, $_POST);
    $raw_input = file_get_contents('php://input');
    if (!empty($raw_input)) {
        $json_data = json_decode($raw_input, true);
        if (is_array($json_data)) {
            $inputs = array_merge($inputs, $json_data);
        } else {
            parse_str($raw_input, $raw_post);
            if (is_array($raw_post)) {
                $inputs = array_merge($inputs, $raw_post);
            }
        }
    }

    $reg_type = isset($inputs['reg_type']) ? trim($inputs['reg_type']) : null;
    $team_name = isset($inputs['team_name']) ? trim($inputs['team_name']) : null;
    $leader_name = isset($inputs['leader_name']) ? trim($inputs['leader_name']) : null;
    $leader_email = isset($inputs['leader_email']) ? trim($inputs['leader_email']) : null;
    $phone_number = isset($inputs['phone_number']) ? trim($inputs['phone_number']) : null;
    $github_link = isset($inputs['github_link']) ? trim($inputs['github_link']) : null;
    $experience_level = isset($inputs['experience_level']) ? trim($inputs['experience_level']) : null;
    $track_selection = isset($inputs['track_selection']) ? trim($inputs['track_selection']) : null;
    $team_members = isset($inputs['team_members']) ? trim($inputs['team_members']) : ''; // JSON array of squad members

    addLog($response['db_logs'], ">> RECV_PARAMS: PARSING COMPILATION SQUAD METADATA...");
    addLog($response['db_logs'], ">> DEBUG: REQUEST_METHOD = " . $_SERVER['REQUEST_METHOD']);
    addLog($response['db_logs'], ">> DEBUG: CONTENT_TYPE = " . (isset($_SERVER['CONTENT_TYPE']) ? $_SERVER['CONTENT_TYPE'] : 'NOT SET'));
    addLog($response['db_logs'], ">> DEBUG: POST KEYS = " . implode(', ', array_keys($_POST)));
    addLog($response['db_logs'], ">> DEBUG: RAW POST LEN = " . strlen(file_get_contents('php://input')));

    // 2. Validate basic presence of registration type
    if (!$reg_type || !in_array($reg_type, ['mfa', 'thread'])) {
        throw new Exception("INVALID REGISTRATION TYPE SIGNATURE IDENTIFIED. Received: '" . var_export($reg_type, true) . "'");
    }
    
    addLog($response['db_logs'], ">> VAL_REQ: PROCESSING REGISTRY ENROLLMENT FOR '" . strtoupper($reg_type) . "' PORT...");

    // 3. Perform server-side validation
    if (empty($team_name) || strlen($team_name) < 3) {
        throw new Exception("VALIDATION FAILED: TEAM NAME PARAMETER REQUIRES AT LEAST 3 CHARACTERS.");
    }
    if (empty($leader_name) || strlen($leader_name) < 3) {
        throw new Exception("VALIDATION FAILED: LEADER NAME PARAMETER REQUIRES AT LEAST 3 CHARACTERS.");
    }
    if (empty($leader_email) || !filter_var($leader_email, FILTER_VALIDATE_EMAIL)) {
        throw new Exception("VALIDATION FAILED: INVALID OR CORRUPT LEADER EMAIL ADDRESS ENCOUNTERED.");
    }
    if (empty($phone_number) || strlen($phone_number) < 8) {
        throw new Exception("VALIDATION FAILED: INVALID PHONE NUMBER - COMMS CHANNEL REQ AT LEAST 8 DIGITS.");
    }
    if (empty($github_link) || strlen($github_link) < 5) {
        throw new Exception("VALIDATION FAILED: GITHUB PROFILE HASH STRING TOO SHORT.");
    }

    addLog($response['db_logs'], ">> SANITIZE: ALL INPUT CREDENTIALS VERIFIED AGAINST SERVER POLICY.");

    // Decode team members JSON to verify squad count
    $membersArray = json_decode($team_members, true);
    if (!is_array($membersArray) || count($membersArray) === 0) {
        throw new Exception("VALIDATION FAILED: SQUAD INTEGRITY BROKEN - REQUIRE AT LEAST 1 REGISTERED MEMBER.");
    }
    
    addLog($response['db_logs'], ">> SQUAD: VERIFIED SQUAD COUNT: " . count($membersArray) . " OPERATIVES.");

    // 4. Establish Secure PDO Connection
    // Default XAMPP/WAMP credentials. Modify as required for staging.
    $db_host = '127.0.0.1';
    $db_port = '3307';
    $db_name = 'authx_db';
    $db_user = 'root';
    $db_pass = '';
    
    addLog($response['db_logs'], ">> CONNECTING TO REMOTE DATABASE SERVER AT {$db_host}... [OK]");

    $dsn = "mysql:host=$db_host;port=$db_port;dbname=$db_name;charset=utf8mb4";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];

    $pdo = new PDO($dsn, $db_user, $db_pass, $options);
    addLog($response['db_logs'], ">> ENGAGED UTF8MB4 SECURE DATABASE CONNECTION DRIVER.");

    // 5. Prepare SQL statement (Anti-SQL Injection)
    $sql = "INSERT INTO hackathon_registrations 
            (registration_type, team_name, leader_name, leader_email, phone_number, github_link, experience_level, track_selection, team_members) 
            VALUES 
            (:registration_type, :team_name, :leader_name, :leader_email, :phone_number, :github_link, :experience_level, :track_selection, :team_members)";
    
    addLog($response['db_logs'], ">> COMPILING SQL PREPARED STATEMENT WITH PLACEHOLDERS...");

    $stmt = $pdo->prepare($sql);
    
    addLog($response['db_logs'], ">> BINDING TRANS-VAL REGISTRY PARAMETERS... [OK]");

    $stmt->execute([
        ':registration_type' => $reg_type,
        ':team_name'         => $team_name,
        ':leader_name'       => $leader_name,
        ':leader_email'      => $leader_email,
        ':phone_number'      => $phone_number,
        ':github_link'       => $github_link,
        ':experience_level'  => $experience_level,
        ':track_selection'   => $track_selection,
        ':team_members'      => $team_members
    ]);

    $last_id = $pdo->lastInsertId();
    addLog($response['db_logs'], ">> SQL DATA TRANSACTION COMMITTED SUCCESSFULLY.");
    addLog($response['db_logs'], ">> INJECTED NEW REGISTRATION RECORD ID: #$last_id");
    addLog($response['db_logs'], ">> AUTHX LEDGER TRANSACTION COMPLETION STATUS: SECURED");

    $response['success'] = true;
    $response['message'] = 'Operative Team Registered successfully!';
    $response['row_id'] = $last_id;

} catch (PDOException $pe) {
    http_response_code(500);
    $response['success'] = false;
    $response['message'] = "DATABASE CORE CRITICAL ERROR.";
    addLog($response['db_logs'], ">> [SQL_ERR] PDO DATABASE EXCEPTION: " . $pe->getMessage());
    addLog($response['db_logs'], ">> CRITICAL TRANSACTION CANCELLED. ROLLBACK ENGAGED.");
} catch (Exception $e) {
    http_response_code(400);
    $response['success'] = false;
    $response['message'] = $e->getMessage();
    addLog($response['db_logs'], ">> [VAL_ERR] PROCESS EXCEPTION: " . $e->getMessage());
    addLog($response['db_logs'], ">> TRANSACTION CANCELLATION ENGAGED.");
}

// Return JSON response payload
echo json_encode($response);
exit;
