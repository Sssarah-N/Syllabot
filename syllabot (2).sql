-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 26, 2025 at 09:00 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `syllabot`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetCoursesBySchool` (IN `p_schoolName` VARCHAR(100))   BEGIN
    SELECT *
    FROM `course`      AS c
    JOIN `department`  AS d
      ON c.departmentName = d.DepartmentName
    WHERE d.schoolName = p_schoolName;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `GetInstructorAverageRating` (IN `instructor_id` INT)   BEGIN
    SELECT AVG(instructorRating) AS avg_rating 
    FROM instructorrating 
    WHERE instructorID = instructor_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getSection` (IN `input_courseID` VARCHAR(20))   BEGIN
    SELECT * 
    FROM section
    WHERE courseid = input_courseID;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getSectionSchedule` (IN `sectionID` INT)   BEGIN
  SELECT
    d.`day`                                  AS day,
    TIME_FORMAT(t.startTime, '%H:%i')       AS start_time,
    TIME_FORMAT(t.endTime,   '%H:%i')       AS end_time
  FROM `sectionDay` AS d
  JOIN `sectionTime` AS t
    ON d.sectionID = t.sectionID
  WHERE d.sectionID = sectionID
  ORDER BY 
    FIELD(d.`day`, 'Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
    t.startTime;
END$$

--
-- Functions
--
CREATE DEFINER=`root`@`localhost` FUNCTION `find_course_sections` (`course_id` VARCHAR(20)) RETURNS INT(11) DETERMINISTIC BEGIN
    DECLARE section_count INT;
    SELECT COUNT(*) INTO section_count
    FROM section
    WHERE courseID = course_id;
    RETURN section_count;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `courseID` varchar(50) DEFAULT NULL,
  `courseName` varchar(255) DEFAULT NULL,
  `departmentName` varchar(100) DEFAULT NULL,
  `credit` float DEFAULT NULL,
  `description` text DEFAULT NULL,
  `courseStatus` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `course`
--

INSERT INTO `course` (`courseID`, `courseName`, `departmentName`, `credit`, `description`, `courseStatus`) VALUES
('CS-UY 394X', 'SPECIAL TOPICS IN COMPUTER SCIENCE', 'Computer Science', 0, 'This variable-credit special topics course is designed for juniors and seniors. Prerequisite: Department’s permission. Additional details and schedule: …', 'Open'),
('CS-UY 410X', 'UNDERGRADUATE GUIDED STUDIES IN COMPUTER SCIENCE', 'Computer Science', 3, 'Students work on an individual basis under the supervision of a faculty member. May be used to substitute for required project courses. (Multiple sections available.)', 'Open'),
('CS-UY 420X', 'UNDERGRADUATE RESEARCH IN COMPUTER SCIENCE', 'Computer Science', 2, 'Research under faculty supervision; may lead to publication or independent study credit. (Multiple sections available.)', 'Open'),
('CS-UY 1113', 'PROBLEM SOLVING AND PROGRAMMING I', 'Computer Science', 3, 'Introduces problem solving and computer programming using Python for engineering students with no prior programming experience. Includes project work and lab exercises.', 'Open'),
('CS-UY 1114', 'INTRO TO PROGRAMMING & PROBLEM SOLVING', 'Computer Science', 4, 'Introduces fundamental programming concepts using Python for CS and CE majors. Emphasizes problem solving, basic data structures, and algorithms.', 'Open'),
('CS-UY 1134', 'DATA STRUCTURES AND ALGORITHMS', 'Computer Science', 4, 'Covers abstract data types, standard data structures, algorithms, and analysis of algorithm efficiency. Prerequisite: CS-UY 1114 or CS-UY 1121 (C- or better).', 'Open'),
('CS-UY 2413', 'DESIGN & ANALYSIS OF ALGORITHMS', 'Computer Science', 3, 'Examines asymptotic notation, algorithm design techniques, and NP-completeness. Emphasizes practical analysis and implementation of algorithms.', 'Open'),
('CS-UY 3083', 'INTRODUCTION TO DATABASES', 'Computer Science', 3, 'Covers relational and object-oriented data models, SQL, database design, and transaction management. Held at 6 MetroTech Center Room 215 with Dey, Ratan. Notes: Enrollment is limited to certain majors. See https://bit.ly/CSEUndergradCrossRegistrationSpring25', 'Open'),
('CS-UY 3224', 'INTRO TO OPERATING SYSTEMS', 'Computer Science', 4, 'Studies operating system components including process scheduling, memory management, and file systems. Involves both theoretical and practical work.', 'Open'),
('CS-UY 3923', 'COMPUTER SECURITY', 'Computer Science', 3, 'Covers cryptographic systems, access control, security protocols, and strategies to mitigate cyber threats. Focuses on both theory and practical applications.', 'Open'),
('CS-UY 3943', 'SPECIAL TOPICS IN COMPUTER SCIENCE', 'Computer Science', 3, 'Special topics course covering emerging areas such as blockchain, cyber security, and advanced algorithms. Content and schedule vary by semester. Prerequisite: Department’s permission.', 'Open'),
('CS-UY 2124', 'OBJECT ORIENTED PROGRAMMING', 'Computer Science', 4, 'Intermediate-level programming course in C++ covering object-oriented concepts, inheritance, polymorphism, and the standard template library (STL).', 'Open'),
('CS-UY 4563', 'INTRODUCTION TO MACHINE LEARNING', 'Computer Science', 3, 'Hands-on introduction to machine learning covering regression, classification, clustering, and neural networks using Python and ML libraries. Prerequisite: CS-UY 1134 and (MA-UY 2314 or equivalent).', 'Open'),
('ACCT-GB 2103', 'Financial Statement Analysis', 'Accounting', 1.5, 'Explains financial accounting from a new angle to provide a foundation for intermediate financial reporting, analysis, and modeling. Includes a framework for analysis with spreadsheets.', 'Open'),
('ACCT-GB 2111', 'Financial Reporting and Disclosure Part 1', 'Accounting', 1.5, 'Uses ratio and accounting analysis to discuss in-depth financial reporting principles and the impact of management decisions on financial statements. Ideal for students targeting careers in investment banking and consulting.', 'Open'),
('ACCT-GB 2112', 'Financial Reporting and Disclosure Part 2', 'Accounting', 1.5, 'Continuation of Part 1, focusing on advanced topics, complex transactions, and disclosure requirements in financial reporting.', 'Open'),
('ACCT-GB 3103', 'Internal Decision Making and Corporate Performance', 'Accounting', 1.5, 'Explores the use of accounting information for internal planning, analysis, and decision-making. Equips students to interpret and act on financial and non-financial reports.', 'Open'),
('BIOL-UA 123', 'Principles of Biology Laboratory', 'Biology', 1, 'Introductory laboratory course exposing students to modern biology approaches – from molecular to organismal levels. Includes hands-on experiments and projects.', 'Open'),
('BIOL-UA 223', 'Molecular and Cell Biology Laboratory', 'Biology', 1, 'Laboratory course applying concepts from molecular and cell biology (BIOL-UA 21) to hands-on experiments such as DNA isolation and electrophoresis.', 'Open'),
('BIOL-UA 9123', 'Principles of Biology Laboratory (NYU London)', 'Biology', 1, 'Laboratory course offered at NYU London covering experimental biology techniques. Students must account for additional commute time.', 'Open'),
('COLIT-GA 1400', 'Sem in Lit:Rsch Mthds Tchnqs', 'Comparative Literature', 4, 'For course description, please see the Comp Lit website at http://complit.as.nyu.edu/object/complit.grad.courses', 'Open'),
('COLIT-GA 1560', 'Contemp Crit Theory: Freud\'s Case Histories', 'Comparative Literature', 4, 'Examines Freud\'s published case histories with supplementary readings from Lacan, Abraham, Torok, and Derrida.', 'Open'),
('COLIT-GA 1732', 'Comp Lit in The Arab Context', 'Comparative Literature', 4, 'Focuses on literature from the Arab context; SAME AS G45.1067 & G77.1712.', 'Wait List'),
('COLIT-GA 2645', 'Aesthetic Practices & Social Criticism', 'Comparative Literature', 2, 'Graduate seminar examining aesthetic practices and social criticism. Topics vary by semester. Taught by Max Czollek in Spring 2024.', 'Open'),
('COLIT-GA 2645', 'Between Berlin & Hollywood: A Cinematic Dialog', 'Comparative Literature', 2, 'Seminar exploring cinematic dialogue between Berlin and Hollywood, focusing on postwar trauma and film noir influences. (Fall 2023)', 'Open'),
('COLIT-GA 2645', 'Plasticity & Anxiety: Philosophy, Psychoanalysis', 'Comparative Literature', 2, 'Interdisciplinary seminar on philosophical and psychoanalytic approaches to plasticity and anxiety. (Fall 2023)', 'Open'),
('COLIT-GA 2192', 'Tpcs Ital Lit: Fantasies of Love', 'Comparative Literature', 4, 'Interdisciplinary approaches to lyric poetry from Early Modern Italy and the history of emotions in literature.', 'Open'),
('COLIT-GA 2192', 'Tpcs Ital Lit: Italian Journeys', 'Comparative Literature', 4, 'Explores Italian travel writing and its impact on narratives regarding the Global South.', 'Open'),
('COLIT-GA 2192', 'Tpcs Ital Lit: Pier Paolo Pasolini and the Politics of Art History', 'Comparative Literature', 4, 'Interdisciplinary seminar examining Pasolini’s role as an art historian and critic, focusing on tradition and political context.', 'Open'),
('COLIT-GA 2453', 'Tpcs in Lit Theory II: Narrative and Nation', 'Comparative Literature', 4, 'Examines the relationship between narrative and national identity using interdisciplinary methods; includes a full reading of Boccaccio’s Decameron.', 'Open'),
('COLIT-GA 2201', 'Literature Seminar: Arts of Attention: Reading Global Modernisms', 'Comparative Literature', 4, 'Explores modernist texts and experimental narrative techniques to understand how literature captures and trains attention.', 'Open'),
('MPAMB-GE 2312', 'Writing in the Music Industry', 'Music Business', 2, 'Provides a practical look at nonfiction writing about music—covering articles, blogs, biographies, liner notes, and press materials—for various roles in the music industry.', 'Open'),
('MPAMB-GE 2314', 'Advanced Topics in Recorded Music and Music Publishing', 'Music Business', 2, 'Examines public policy and business impacts of music publishers and record labels, from copyright creation to revenue generation.', 'Open'),
('TCSM1-UC 2100', 'Public Relations in Sport', 'Sport Management', 3, 'Analyzes information management processes in the sport industry, emphasizing effective communication between sport organizations and stakeholders. Includes projects, presentations, and written assignments.', 'Closed'),
('TCSM1-UC 2120', 'Sport Media Storytelling', 'Sport Management', 3, 'Introduces sport multimedia storytelling through news gathering, writing, and digital content creation (including podcasting). Prerequisite: TCSM1-UC 2100 and two writing courses.', 'Open'),
('TCSM1-UC 2320', 'Sports Law', 'Sport Management', 3, 'Survey of legal issues in sports including contractual analysis, player relations, agent regulation, and collective bargaining. Multiple sections available.', 'Open'),
('TCSM1-UC 2330', 'Sports Facility Management', 'Sport Management', 3, 'Examines planning, operation, maintenance, and pricing of sports facilities such as stadiums and arenas.', 'Open'),
('TCSM1-UC 2355', 'Revenue Generation in Sport', 'Sport Management', 3, 'Analyzes revenue streams in sport organizations including ticketing, licensing, sponsorships, and merchandising. Also discusses dynamic pricing and secondary markets.', 'Open'),
('NEURL-UA 211', 'Cellular & Molecular Neurobiology Lab', 'Neural Science', 2, 'Provides broad exposure to experimental approaches in cellular neuroscience. Laboratories focus on cell structure, CNS organization, and neural signaling. Prerequisites: Intro to Neural Science; CoReq/PreReq: Molec Cell Bio I and CMNB.', 'Closed'),
('NEURL-UA 221', 'Behavioral & Integrative Neuroscience Lab', 'Neural Science', 2, 'Addresses the physiological and anatomical bases of behavior through laboratory experiments on sensory, motor, and motivational mechanisms. Prerequisites: PSYCH-UA.0001, BIOL-UA.0011, BIOL-UA.0012, PSYCH-UA.0024 or NEURL-UA.0100.', 'Open');

-- --------------------------------------------------------

--
-- Table structure for table `department`
--

CREATE TABLE `department` (
  `DepartmentName` varchar(100) NOT NULL,
  `schoolName` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `department`
--

INSERT INTO `department` (`DepartmentName`, `schoolName`) VALUES
('Biology', 'College of Arts and Science'),
('Comparative Literature', 'College of Arts and Science'),
('Neural Science', 'College of Arts and Science'),
('Accounting', 'Leonard N. Stern School of Business'),
('Music Business', 'Steinhardt School of Culture, Education, and Human Development'),
('Sport Management', 'Steinhardt School of Culture, Education, and Human Development'),
('Civil and Urban Engineering', 'Tandon School of Engineering'),
('Computer Science', 'Tandon School of Engineering'),
('Engineering', 'Tandon School of Engineering'),
('Mechanical and Aerospace Engineering', 'Tandon School of Engineering');

-- --------------------------------------------------------

--
-- Table structure for table `enrollment`
--

CREATE TABLE `enrollment` (
  `studentID` varchar(10) NOT NULL,
  `sectionID` int(11) NOT NULL,
  `enrollStatus` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `instructor`
--

CREATE TABLE `instructor` (
  `instructorID` int(11) NOT NULL,
  `instructorName` varchar(100) DEFAULT NULL,
  `departmentName` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `instructor`
--

INSERT INTO `instructor` (`instructorID`, `instructorName`, `departmentName`) VALUES
(1, 'Ratan Dey', 'Computer Science'),
(2, 'Romero Cruz, Sebastian', 'Computer Science'),
(3, 'DePasquale, Peter', 'Computer Science'),
(4, 'Tal, Itay', 'Computer Science'),
(5, 'Hellerstein, Lisa', 'Computer Science'),
(6, 'Kiani, Ayesha', 'Computer Science'),
(7, 'Sterling, John', 'Computer Science'),
(8, 'Sandoval, Gustavo', 'Computer Science'),
(9, 'Cappos, Justin', 'Computer Science'),
(10, 'Sellie, Linda', 'Computer Science'),
(11, 'Wayne, Rachel', 'Biology'),
(12, 'Michael Roberts', 'Accounting'),
(13, 'Sarah Lee', 'Accounting'),
(14, 'David Kim', 'Biology'),
(15, 'Maria Garcia', 'Comparative Literature'),
(16, 'John White', 'Comparative Literature'),
(17, 'Andrea Murphy', 'Music Business'),
(18, 'Daniel Green', 'Music Business'),
(19, 'Susan Brown', 'Neural Science'),
(20, 'James Wilson', 'Neural Science'),
(21, 'Jane Smith', 'Sport Management');

-- --------------------------------------------------------

--
-- Table structure for table `instructorrating`
--

CREATE TABLE `instructorrating` (
  `ratingID` int(11) NOT NULL,
  `instructorRating` int(11) DEFAULT NULL,
  `instructorID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `instructorrating`
--

INSERT INTO `instructorrating` (`ratingID`, `instructorRating`, `instructorID`) VALUES
(1, 5, 1),
(2, 4, 2),
(3, 4, 3),
(4, 5, 4),
(5, 4, 5),
(6, 5, 6),
(7, 4, 7),
(8, 5, 8),
(9, 4, 9),
(10, 4, 10),
(11, 5, 11),
(12, 3, 12),
(13, 4, 13),
(14, 1, 14),
(15, 3, 15),
(16, 4, 16),
(17, 5, 17),
(18, 2, 18),
(19, 5, 19),
(20, 3, 20),
(21, 5, 21);

-- --------------------------------------------------------

--
-- Table structure for table `location`
--

CREATE TABLE `location` (
  `address` varchar(200) NOT NULL,
  `schoolName` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `location`
--

INSERT INTO `location` (`address`, `schoolName`) VALUES
('Brooklyn Campus', 'Tandon School of Engineering'),
('NYU London (Global)', 'College of Arts and Science'),
('Washington Square', 'College of Arts and Science'),
('Washington Square', 'Leonard N. Stern School of Business'),
('Washington Square', 'Steinhardt School of Culture, Education, and Human Development - Graduate');

-- --------------------------------------------------------

--
-- Table structure for table `login`
--

CREATE TABLE `login` (
  `StudentID` varchar(10) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `major`
--

CREATE TABLE `major` (
  `majorName` varchar(100) NOT NULL,
  `departmentName` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `major`
--

INSERT INTO `major` (`majorName`, `departmentName`) VALUES
('Accounting', 'Accounting'),
('Biology', 'Biology'),
('Comparative Literature', 'Comparative Literature'),
('Computer Science', 'Computer Science'),
('Computer Science and Engineering', 'Computer Science'),
('Cybersecurity', 'Computer Science'),
('Data Science', 'Computer Science'),
('Music Business', 'Music Business'),
('Neural Science', 'Neural Science'),
('Sport Management', 'Sport Management');

-- --------------------------------------------------------

--
-- Table structure for table `school`
--

CREATE TABLE `school` (
  `schoolName` varchar(100) NOT NULL,
  `schoolAddress` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `school`
--

INSERT INTO `school` (`schoolName`, `schoolAddress`) VALUES
('College of Arts and Science', 'Washington Square'),
('Graduate School of Arts and Science', 'Washington Square'),
('Leonard N. Stern School of Business', 'Washington Square'),
('School of Professional Studies', 'Washington Square'),
('Steinhardt School of Culture, Education, and Human Development', 'Washington Square'),
('Steinhardt School of Culture, Education, and Human Development - Graduate', 'Washington Square'),
('Tandon School of Engineering', '6 MetroTech Center');

-- --------------------------------------------------------

--
-- Table structure for table `section`
--

CREATE TABLE `section` (
  `sectionID` int(11) NOT NULL,
  `courseID` varchar(20) DEFAULT NULL,
  `instructorID` int(11) DEFAULT NULL,
  `termID` varchar(8) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `sectionType` varchar(20) DEFAULT NULL,
  `sectionNo` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `section`
--

INSERT INTO `section` (`sectionID`, `courseID`, `instructorID`, `termID`, `address`, `sectionType`, `sectionNo`) VALUES
(2808, 'TCSM1-UC 2100', 21, 'SU2024', 'Distance Learning/Synchronous', 'Lecture', '001'),
(3295, 'COLIT-GA 1400', 15, 'F2023', 'Washington Square', 'Seminar', '001'),
(7835, 'CS-UY 3923', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'I'),
(7973, 'CS-UY 3943', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'A'),
(8126, 'CS-UY 1114', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'ALEC'),
(8148, 'CS-UY 2413', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'A'),
(8160, 'CS-UY 1134', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'ALEC'),
(8170, 'CS-UY 2124', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'ALEC'),
(8182, 'CS-UY 4563', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'A'),
(8183, 'CS-UY 410X', 2, 'S2025', 'Brooklyn Campus', 'Guided Studies', 'BK01'),
(8184, 'CS-UY 410X', 2, 'S2025', 'Brooklyn Campus', 'Guided Studies', 'BK02'),
(8193, 'CS-UY 420X', 2, 'S2025', 'Brooklyn Campus', 'Research', 'BK01'),
(8194, 'CS-UY 420X', 2, 'S2025', 'Brooklyn Campus', 'Research', 'BK02'),
(8203, 'CS-UY 1113', 2, 'S2025', 'Brooklyn Campus', 'Lecture', 'ALEC'),
(8643, 'COLIT-GA 1560', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(8644, 'COLIT-GA 2201', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(10236, 'TCSM1-UC 2320', 21, 'F2023', 'Washington Square', 'Lecture', '001'),
(10282, 'TCSM1-UC 2330', 21, 'F2023', 'Washington Square', 'Lecture', '001'),
(10428, 'CS-UY 3083', 2, 'F2023', 'Brooklyn Campus', 'Lecture', 'A'),
(10429, 'TCSM1-UC 2355', 21, 'F2023', 'Washington Square', 'Lecture', '001'),
(10521, 'TCSM1-UC 2100', 21, 'F2023', 'Washington Square', 'Lecture', '002'),
(10522, 'TCSM1-UC 2120', 21, 'F2023', 'Washington Square', 'Lecture', '001'),
(10530, 'TCSM1-UC 2355', 21, 'SU2024', 'Distance Learning/Synchronous', 'Lecture', '001'),
(12739, 'MPAMB-GE 2312', 17, 'F2024', 'Washington Square', 'Lecture', '001'),
(14168, 'BIOL-UA 123', 11, 'S2024', 'Washington Square', 'Laboratory', '001'),
(14170, 'BIOL-UA 223', 14, 'S2024', 'Washington Square', 'Laboratory', '001'),
(14180, 'BIOL-UA 9123', 11, 'S2024', 'NYU London (Global)', 'Laboratory', 'L01'),
(15000, 'ACCT-GB 2103', 12, 'F2023', 'Washington Square', 'Lecture', '001'),
(15009, 'TCSM1-UC 2320', 21, 'S2024', 'Washington Square', 'Lecture', '001'),
(15010, 'ACCT-GB 2111', 12, 'F2023', 'Washington Square', 'Lecture', '001'),
(15011, 'TCSM1-UC 2320', 21, 'S2024', 'Online', 'Lecture', '002'),
(15020, 'ACCT-GB 2112', 12, 'S2024', 'Washington Square', 'Lecture', '001'),
(15030, 'ACCT-GB 3103', 12, 'S2024', 'Washington Square', 'Lecture', '001'),
(15057, 'TCSM1-UC 2100', 21, 'S2024', 'Washington Square', 'Lecture', '001'),
(15114, 'TCSM1-UC 2100', 21, 'S2024', 'Washington Square', 'Lecture', '002'),
(19206, 'COLIT-GA 1732', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(20164, 'COLIT-GA 2645', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(20985, 'COLIT-GA 2192', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(20986, 'COLIT-GA 2192', 15, 'S2024', 'Washington Square', 'Seminar', '002'),
(21273, 'COLIT-GA 2192', 15, 'S2024', 'Washington Square', 'Seminar', '001'),
(21631, 'MPAMB-GE 2314', 17, 'F2024', 'Washington Square', 'Lecture', '001'),
(22781, 'COLIT-GA 2453', 15, 'F2023', 'Washington Square', 'Lecture', '001'),
(22854, 'COLIT-GA 2645', 15, 'F2023', 'Washington Square', 'Seminar', '001'),
(22855, 'COLIT-GA 2645', 15, 'F2023', 'Washington Square', 'Seminar', '002'),
(23148, 'COLIT-GA 2453', 15, 'F2023', 'Washington Square', 'Lecture', '002');

-- --------------------------------------------------------

--
-- Table structure for table `sectionday`
--

CREATE TABLE `sectionday` (
  `day` varchar(10) NOT NULL,
  `sectionID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sectionday`
--

INSERT INTO `sectionday` (`day`, `sectionID`) VALUES
('Mon', 2808),
('Tue', 3295),
('Fri', 7973),
('Mon', 8126),
('Mon', 8148),
('Mon', 8160),
('Mon', 8170),
('Tue', 8182),
('Mon', 8203),
('Mon', 8643),
('Wed', 8644),
('Mon', 10236),
('Mon', 10282),
('Mon', 10428),
('Mon', 10429),
('Tue', 10521),
('Mon', 10522),
('Tue', 10530),
('Tue', 12739),
('Wed', 14168),
('Mon', 14170),
('Tue', 14180),
('Tue', 15009),
('Fri', 15011),
('Mon', 15057),
('Tue', 15114),
('Wed', 19206),
('Mon', 20164),
('Mon', 20985),
('Tue', 20986),
('Fri', 21273),
('Thu', 21631),
('Thu', 22781),
('Fri', 22854),
('Thu', 22855),
('Wed', 23148);

-- --------------------------------------------------------

--
-- Table structure for table `sectiontime`
--

CREATE TABLE `sectiontime` (
  `startTime` time NOT NULL DEFAULT '00:00:00',
  `endTime` time NOT NULL DEFAULT '23:59:59',
  `sectionID` int(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sectiontime`
--

INSERT INTO `sectiontime` (`startTime`, `endTime`, `sectionID`) VALUES
('08:00:00', '09:15:00', 10282),
('08:00:00', '09:20:00', 8183),
('08:00:00', '09:20:00', 8184),
('08:00:00', '09:20:00', 8203),
('09:00:00', '10:15:00', 10236),
('09:00:00', '10:15:00', 12739),
('09:00:00', '10:30:00', 14180),
('09:30:00', '10:45:00', 10429),
('09:30:00', '10:50:00', 8170),
('09:30:00', '11:00:00', 8643),
('10:00:00', '11:15:00', 10428),
('10:00:00', '11:30:00', 19206),
('10:00:00', '11:30:00', 20985),
('10:30:00', '11:45:00', 10521),
('10:30:00', '11:45:00', 15009),
('10:30:00', '11:45:00', 21631),
('11:00:00', '12:15:00', 8182),
('11:00:00', '12:20:00', 8126),
('11:00:00', '12:20:00', 8148),
('11:00:00', '12:20:00', 8160),
('11:00:00', '12:30:00', 20986),
('11:00:00', '13:00:00', 14168),
('11:00:00', '13:30:00', 7973),
('12:00:00', '13:00:00', 15011),
('12:00:00', '13:15:00', 8644),
('12:00:00', '13:15:00', 10522),
('12:00:00', '13:30:00', 21273),
('13:00:00', '14:15:00', 2808),
('13:00:00', '14:30:00', 20164),
('14:00:00', '15:15:00', 15057),
('14:00:00', '15:30:00', 8193),
('14:00:00', '15:30:00', 8194),
('14:00:00', '16:00:00', 3295),
('14:00:00', '16:00:00', 14170),
('14:30:00', '16:00:00', 22781),
('15:00:00', '16:15:00', 10530),
('15:00:00', '16:30:00', 22854),
('15:30:00', '16:45:00', 15114),
('16:00:00', '17:00:00', 22855),
('16:30:00', '18:00:00', 23148);

-- --------------------------------------------------------

--
-- Table structure for table `selected_courses`
--

CREATE TABLE `selected_courses` (
  `studentID` varchar(10) NOT NULL,
  `sectionID` int(11) NOT NULL,
  `dateSelected` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers `selected_courses`
--
DELIMITER $$
CREATE TRIGGER `before_insert_selected_courses` BEFORE INSERT ON `selected_courses` FOR EACH ROW BEGIN
    -- Variable to store conflict count
    DECLARE conflict_count INT;
    
    -- Check for time conflicts
    SELECT COUNT(*) INTO conflict_count
    FROM selected_courses sc
    JOIN section sec1 ON sc.sectionID = sec1.sectionID
    JOIN course c1 ON sec1.courseID = c1.courseID
    JOIN sectionday sd1 ON c1.courseID = sd1.courseID
    JOIN sectiontime st1 ON c1.courseID = st1.courseID,
    section sec2
    JOIN course c2 ON sec2.courseID = c2.courseID
    JOIN sectionday sd2 ON c2.courseID = sd2.courseID
    JOIN sectiontime st2 ON c2.courseID = st2.courseID
    WHERE sc.studentID = NEW.studentID
    AND sec2.sectionID = NEW.sectionID
    AND sd1.day = sd2.day
    AND (
        (st1.startTime <= st2.endTime AND st2.startTime <= st1.endTime)
    );

    -- If there's a conflict, raise an error with details
    IF conflict_count > 0 THEN
        -- Get the conflicting course details
        SET @conflict_details = (
            SELECT CONCAT(
                'Time conflict with: ',
                GROUP_CONCAT(
                    CONCAT(
                        c1.courseID, 
                        ' on ', 
                        sd1.day, 
                        ' at ', 
                        TIME_FORMAT(st1.startTime, '%h:%i %p'),
                        ' - ',
                        TIME_FORMAT(st1.endTime, '%h:%i %p')
                    )
                )
            )
            FROM selected_courses sc
            JOIN section sec1 ON sc.sectionID = sec1.sectionID
            JOIN course c1 ON sec1.courseID = c1.courseID
            JOIN sectionday sd1 ON c1.courseID = sd1.courseID
            JOIN sectiontime st1 ON c1.courseID = st1.courseID,
            section sec2
            JOIN course c2 ON sec2.courseID = c2.courseID
            JOIN sectionday sd2 ON c2.courseID = sd2.courseID
            JOIN sectiontime st2 ON c2.courseID = st2.courseID
            WHERE sc.studentID = NEW.studentID
            AND sec2.sectionID = NEW.sectionID
            AND sd1.day = sd2.day
            AND (
                (st1.startTime <= st2.endTime AND st2.startTime <= st1.endTime)
            )
        );
        
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = @conflict_details;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE `student` (
  `StudentID` varchar(10) NOT NULL,
  `schoolname` varchar(100) DEFAULT NULL,
  `majorName` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `currentLevel` varchar(20) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `dateOfBirth` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student`
--

INSERT INTO `student` (`StudentID`, `schoolname`, `majorName`, `name`, `currentLevel`, `email`, `dateOfBirth`) VALUES
('S001', 'Tandon School of Engineering', 'Computer Science and Engineering', 'Alice Johnson', 'Freshman', 'alice.johnson@nyu.edu', '2003-04-15'),
('S002', 'College of Arts and Science', 'Biology', 'Bob Smith', 'Sophomore', 'bob.smith@nyu.edu', '2002-09-10'),
('S003', 'Leonard N. Stern School of Business', 'Accounting', 'Catherine Lee', 'Graduate', 'catherine.lee@nyu.edu', '1999-12-05'),
('S004', 'Steinhardt School of Culture, Education, and Human Development - Graduate', 'Music Business', 'David Martinez', 'Graduate', 'david.martinez@nyu.edu', '1998-06-20'),
('S005', 'Graduate School of Arts and Science', 'Comparative Literature', 'Eva Green', 'Graduate', 'eva.green@nyu.edu', '1997-11-30'),
('S006', 'School of Professional Studies', 'Sport Management', 'Frank O\'Connor', 'Senior', 'frank.oconnor@nyu.edu', '2000-01-25'),
('S007', 'Tandon School of Engineering', 'Cybersecurity', 'Grace Kim', 'Sophomore', 'grace.kim@nyu.edu', '2003-07-14'),
('S008', 'Tandon School of Engineering', 'Data Science', 'Henry White', 'Junior', 'henry.white@nyu.edu', '2001-03-11'),
('S009', 'Tandon School of Engineering', 'Computer Science', 'Irene Zhang', 'Senior', 'irene.zhang@nyu.edu', '2000-08-22'),
('S010', 'College of Arts and Science', 'Neural Science', 'James Thompson', 'Junior', 'james.thompson@nyu.edu', '2001-05-05');

-- --------------------------------------------------------

--
-- Table structure for table `temp_cart`
--

CREATE TABLE `temp_cart` (
  `session_id` varchar(36) NOT NULL,
  `sectionID` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `temp_cart`
--

INSERT INTO `temp_cart` (`session_id`, `sectionID`, `created_at`) VALUES
('5c1b1b7d-0566-4a32-8ceb-9644c387a29c', 14180, '2025-04-26 14:47:14');

-- --------------------------------------------------------

--
-- Table structure for table `term`
--

CREATE TABLE `term` (
  `termid` varchar(8) NOT NULL,
  `startDate` date DEFAULT NULL,
  `endDate` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `term`
--

INSERT INTO `term` (`termid`, `startDate`, `endDate`) VALUES
('F2023', '2023-09-05', '2023-12-15'),
('F2024', '2024-09-03', '2024-12-12'),
('S2024', '2024-01-21', '2024-05-06'),
('S2025', '2025-01-21', '2025-05-06'),
('SU2024', '2024-05-20', '2024-07-01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `department`
--
ALTER TABLE `department`
  ADD PRIMARY KEY (`DepartmentName`),
  ADD KEY `schoolName` (`schoolName`);

--
-- Indexes for table `enrollment`
--
ALTER TABLE `enrollment`
  ADD PRIMARY KEY (`studentID`,`sectionID`),
  ADD KEY `sectionID` (`sectionID`);

--
-- Indexes for table `instructor`
--
ALTER TABLE `instructor`
  ADD PRIMARY KEY (`instructorID`),
  ADD KEY `departmentName` (`departmentName`);

--
-- Indexes for table `instructorrating`
--
ALTER TABLE `instructorrating`
  ADD PRIMARY KEY (`ratingID`),
  ADD KEY `instructorID` (`instructorID`);

--
-- Indexes for table `location`
--
ALTER TABLE `location`
  ADD PRIMARY KEY (`address`,`schoolName`),
  ADD KEY `schoolName` (`schoolName`);

--
-- Indexes for table `login`
--
ALTER TABLE `login`
  ADD PRIMARY KEY (`StudentID`,`password_hash`);

--
-- Indexes for table `major`
--
ALTER TABLE `major`
  ADD PRIMARY KEY (`majorName`),
  ADD KEY `departmentName` (`departmentName`);

--
-- Indexes for table `school`
--
ALTER TABLE `school`
  ADD PRIMARY KEY (`schoolName`);

--
-- Indexes for table `section`
--
ALTER TABLE `section`
  ADD PRIMARY KEY (`sectionID`),
  ADD KEY `courseID` (`courseID`),
  ADD KEY `instructorID` (`instructorID`),
  ADD KEY `termID` (`termID`),
  ADD KEY `address` (`address`);

--
-- Indexes for table `sectionday`
--
ALTER TABLE `sectionday`
  ADD PRIMARY KEY (`sectionID`,`day`) USING BTREE,
  ADD UNIQUE KEY `fk_sectionday_section` (`sectionID`) USING BTREE;

--
-- Indexes for table `sectiontime`
--
ALTER TABLE `sectiontime`
  ADD PRIMARY KEY (`startTime`,`endTime`,`sectionID`) USING BTREE,
  ADD KEY `fk_sectiontime_section` (`sectionID`);

--
-- Indexes for table `selected_courses`
--
ALTER TABLE `selected_courses`
  ADD PRIMARY KEY (`studentID`,`sectionID`),
  ADD KEY `selected_courses_ibfk_2` (`sectionID`);

--
-- Indexes for table `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`StudentID`),
  ADD KEY `schoolname` (`schoolname`),
  ADD KEY `majorName` (`majorName`);

--
-- Indexes for table `temp_cart`
--
ALTER TABLE `temp_cart`
  ADD PRIMARY KEY (`session_id`,`sectionID`),
  ADD KEY `sectionID` (`sectionID`);

--
-- Indexes for table `term`
--
ALTER TABLE `term`
  ADD PRIMARY KEY (`termid`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `enrollment`
--
ALTER TABLE `enrollment`
  ADD CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`studentID`) REFERENCES `student` (`StudentID`),
  ADD CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`sectionID`) REFERENCES `section` (`sectionID`);

--
-- Constraints for table `instructor`
--
ALTER TABLE `instructor`
  ADD CONSTRAINT `instructor_ibfk_1` FOREIGN KEY (`departmentName`) REFERENCES `department` (`DepartmentName`);

--
-- Constraints for table `instructorrating`
--
ALTER TABLE `instructorrating`
  ADD CONSTRAINT `instructorrating_ibfk_1` FOREIGN KEY (`instructorID`) REFERENCES `instructor` (`instructorID`);

--
-- Constraints for table `location`
--
ALTER TABLE `location`
  ADD CONSTRAINT `location_ibfk_1` FOREIGN KEY (`schoolName`) REFERENCES `school` (`schoolName`);

--
-- Constraints for table `login`
--
ALTER TABLE `login`
  ADD CONSTRAINT `login_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `major`
--
ALTER TABLE `major`
  ADD CONSTRAINT `major_ibfk_1` FOREIGN KEY (`departmentName`) REFERENCES `department` (`DepartmentName`);

--
-- Constraints for table `sectionday`
--
ALTER TABLE `sectionday`
  ADD CONSTRAINT `fk_sectionday_section` FOREIGN KEY (`sectionID`) REFERENCES `section` (`sectionID`);

--
-- Constraints for table `selected_courses`
--
ALTER TABLE `selected_courses`
  ADD CONSTRAINT `selected_courses_ibfk_1` FOREIGN KEY (`studentID`) REFERENCES `student` (`StudentID`),
  ADD CONSTRAINT `selected_courses_ibfk_2` FOREIGN KEY (`sectionID`) REFERENCES `section` (`sectionID`);

--
-- Constraints for table `student`
--
ALTER TABLE `student`
  ADD CONSTRAINT `student_ibfk_1` FOREIGN KEY (`schoolname`) REFERENCES `school` (`schoolName`),
  ADD CONSTRAINT `student_ibfk_2` FOREIGN KEY (`majorName`) REFERENCES `major` (`majorName`);

--
-- Constraints for table `temp_cart`
--
ALTER TABLE `temp_cart`
  ADD CONSTRAINT `temp_cart_ibfk_1` FOREIGN KEY (`sectionID`) REFERENCES `section` (`sectionID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
