-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: gearshop
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto_id` int NOT NULL,
  `comprador_cpf` varchar(14) COLLATE utf8mb4_unicode_ci NOT NULL,
  `preco` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_compras_comprador` (`comprador_cpf`),
  KEY `idx_compras_produto` (`produto_id`),
  CONSTRAINT `fk_compras_comprador` FOREIGN KEY (`comprador_cpf`) REFERENCES `usuarios` (`cpf`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_compras_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (1,1,'021.021.021-21',125.00,'2025-11-23 13:01:24');
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `categoria` enum('motor','suspensao','eletrica','iluminacao','interno','lataria','rodas','acessorios') COLLATE utf8mb4_unicode_ci NOT NULL,
  `preco` decimal(10,2) NOT NULL,
  `condicao` enum('novo','seminovo','usado') COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `localizacao` char(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `imagem_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '/static/uploads/placeholder.png',
  `status` enum('ativo','vendido') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ativo',
  `usuario_cpf` varchar(14) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_produtos_usuario` (`usuario_cpf`),
  KEY `idx_produtos_categoria` (`categoria`),
  KEY `idx_produtos_condicao` (`condicao`),
  KEY `idx_produtos_status` (`status`),
  CONSTRAINT `fk_produtos_usuario` FOREIGN KEY (`usuario_cpf`) REFERENCES `usuarios` (`cpf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
INSERT INTO `produtos` VALUES (1,'Pneu careca','rodas',125.00,'usado','Sem condições de uso','GO','/static/uploads/910f40cfa04245f4a9d89ab9da67cb05.jpg','vendido','021.021.021-21','2025-11-23 12:59:56'),(2,'Retrovisor velho','acessorios',75.00,'usado','Retrovisor quebrado','MS','/static/uploads/3e114283a0d841ac9c868f3729b20d52.jpg','ativo','021.021.021-21','2025-11-23 13:00:35'),(3,'Volante esportivo','suspensao',305.00,'seminovo','Volante esportivo','MT','/static/uploads/9235b2edb6df4ff08e9e6c69567a300a.jpg','ativo','021.021.021-21','2025-11-23 13:01:04');
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `cpf` varchar(14) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `senha` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nascimento` date NOT NULL,
  `endereco` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cpf`),
  UNIQUE KEY `uq_usuarios_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES ('021.021.021-21','Pedro José','pedro@gmail.com','(66) 99999-6363','scrypt:32768:8:1$Q9OiZ3C9Iv5vtmdf$84f84e1a90ce4f2cbca801f491b5ed2394e29240c79fec9218fd480c834bb77a510f7a810c8c4559fd51c0eba62a6f8d9c0b5338c8d89e1f947ffddb6a85fe5c','2000-01-01','Rua A, 23 - Centro - Rondonópolis - MT','2025-11-23 12:57:23','2025-11-23 12:57:23'),('085.085.085-85','José da Silva','jose@gmail.com','(66) 99632-5201','scrypt:32768:8:1$aXfj8lYETswXnUGZ$28cf84e75a04577bd7ac5d71c475f2c7000dfdadc0c90e8aa21580f84dd537160274baa864395b53ac874a9f0fd1a0e2cfa1e71a0e6aebc75ec9d28dfec24ea3','2000-02-01','Rua B, 23 - Centro - Cuiabá - MT','2025-11-23 12:59:20','2025-11-23 12:59:20');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-23  9:30:06
