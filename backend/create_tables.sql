-- 퇴직자 취미 추천 시스템 데이터베이스 스키마

-- 1. 사용자 테이블
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    gender ENUM('male', 'female', 'other'),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 설문 질문 테이블
CREATE TABLE survey_questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type ENUM('scale', 'choice', 'binary') NOT NULL,
    category VARCHAR(50) NOT NULL COMMENT '활동성향, 사회성향, 학습성향 등',
    options JSON COMMENT '선택형 질문의 옵션들',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 설문 응답 테이블
CREATE TABLE survey_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES survey_questions(question_id) ON DELETE CASCADE,
    INDEX idx_user_question (user_id, question_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 사용자 프로필 테이블 (설문 결과 분석)
CREATE TABLE user_profiles (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    outdoor_preference DECIMAL(3,2) DEFAULT 0 COMMENT '0-1 scale',
    social_preference DECIMAL(3,2) DEFAULT 0 COMMENT '0-1 scale',
    creative_preference DECIMAL(3,2) DEFAULT 0 COMMENT '0-1 scale',
    learning_preference DECIMAL(3,2) DEFAULT 0 COMMENT '0-1 scale',
    physical_activity DECIMAL(3,2) DEFAULT 0 COMMENT '0-1 scale',
    budget_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 취미 마스터 테이블
CREATE TABLE hobbies (
    hobby_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL COMMENT '미술, 스포츠, 공예, 음악 등',
    description TEXT,
    difficulty_level INT DEFAULT 1 COMMENT '1-5 scale',
    indoor_outdoor ENUM('indoor', 'outdoor', 'both') DEFAULT 'both',
    social_individual ENUM('social', 'individual', 'both') DEFAULT 'both',
    required_budget ENUM('low', 'medium', 'high') DEFAULT 'medium',
    time_commitment VARCHAR(50) COMMENT '주당 필요 시간',
    physical_intensity INT DEFAULT 1 COMMENT '1-5 scale',
    creativity_level INT DEFAULT 1 COMMENT '1-5 scale',
    tutorial_video_url VARCHAR(500),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_difficulty (difficulty_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 취미 키워드 테이블 (검색 및 추천용)
CREATE TABLE hobby_keywords (
    keyword_id INT AUTO_INCREMENT PRIMARY KEY,
    hobby_id INT NOT NULL,
    keyword VARCHAR(50) NOT NULL,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(hobby_id) ON DELETE CASCADE,
    INDEX idx_keyword (keyword),
    INDEX idx_hobby_keyword (hobby_id, keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 사용자 취미 평가 테이블
CREATE TABLE user_hobby_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    hobby_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    experienced BOOLEAN DEFAULT FALSE COMMENT '직접 체험했는지 여부',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(hobby_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_hobby (user_id, hobby_id),
    INDEX idx_hobby_rating (hobby_id, rating),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. 모임/동아리 정보 테이블
CREATE TABLE gatherings (
    gathering_id INT AUTO_INCREMENT PRIMARY KEY,
    hobby_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200),
    region VARCHAR(50) COMMENT '시/도',
    district VARCHAR(50) COMMENT '구/군',
    meeting_type ENUM('online', 'offline', 'hybrid') DEFAULT 'offline',
    schedule_info TEXT COMMENT '정기 모임 일정',
    member_count INT DEFAULT 0,
    contact_info VARCHAR(200),
    website_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(hobby_id) ON DELETE CASCADE,
    INDEX idx_hobby_location (hobby_id, region),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. 추천 기록 테이블 (ML 모델 학습용)
CREATE TABLE recommendation_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    hobby_id INT NOT NULL,
    match_score DECIMAL(5,2) COMMENT '0-100 scale',
    algorithm_version VARCHAR(20),
    was_clicked BOOLEAN DEFAULT FALSE,
    was_rated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(hobby_id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. 시스템 설정 테이블
CREATE TABLE system_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;