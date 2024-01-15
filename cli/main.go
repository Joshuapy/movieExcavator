// 命令行交互
// joshua
// 2023.9.21

package main

import (
	"flag"
	"fmt"
	"log"
	"moviecli/DBdriver"
	"os"
)

const ENV_DBFILE string = "MOVIE_DB"

func showDownloadingMovies(isShow bool, dbfile string) {
	if isShow {
		fmt.Println("=== 下载中的电影 ===")
		DBdriver.ShowDownloadingMovies(dbfile)
	}
}

func showUnlikedMovies(limit int, dbfile string) {
	if limit > 0 {
		fmt.Println("=== 标记忽略 ===")
		DBdriver.ShowUnlinkedMovies(limit, dbfile)
	}
}

func showDoneMovies(limit int, dbfile string) {
	if limit > 0 {
		fmt.Println("=== 下载完成 ===")
		DBdriver.ShowDoneMovies(limit, dbfile)
	}
}

func setStatus(hashes []string, status int, dbfile string) {
	L := 5
	if n := len(hashes); n > L || n < 1 {
		fmt.Printf("一次至少一个或最多设置%d个!\n", L)
		os.Exit(0)
	}
	if status > 4 {
		fmt.Printf("dest_status 取值范围为 0~4, 输入: %d\n", status)
		os.Exit(0)
	}
	DBdriver.SetStatus(hashes, status, dbfile)
}

func showDetailmovie(hashes []string, dbfile string) {
	if n := len(hashes); n != 1 {
		fmt.Println("mush and only one hash", 1)
		os.Exit(0)
	}
	DBdriver.ShowDetailMovie(dbfile, hashes[0])
}

func get_dbfile(cmd_dbfile string) (dbfile string) {
	env_dbfile := os.Getenv(ENV_DBFILE)

	// db文件选择，优先cmd指定
	if cmd_dbfile != "" {
		dbfile = cmd_dbfile
		fmt.Println("cmd_dbfile:", cmd_dbfile)
	} else if env_dbfile != "" {
		dbfile = env_dbfile
		fmt.Println("env_dbfile:", env_dbfile)
	} else {
		log.Fatal("dbfile is empty!, U can use -s /x/y/movies.db or set env MOVIE_DB=/x/y/movies.db")
	}
	return
}

func main() {
	var dbfile string

	// 子命令 show
	showCmd := flag.NewFlagSet("show", flag.ExitOnError)
	var isShowDownloading bool
	var limit int
	var showDoneBylimit int
	var cmd_dbfile string
	showCmd.BoolVar(&isShowDownloading, "d", false, "Is show all downloading movies")
	showCmd.IntVar(&limit, "i", 0, "show the unliked movies with last [n] rows order by create_time")
	showCmd.IntVar(&showDoneBylimit, "w", 0, "show the downloaded movies with last [n] rows order by create_time")
	showCmd.StringVar(&cmd_dbfile, "db", "", "special dbfile for query.")

	// 子命令 reset
	resetCmd := flag.NewFlagSet("reset", flag.ExitOnError)
	var dest_status int
	resetCmd.IntVar(&dest_status, "dst", 2, "reset the status to [dst] with special hash of movie, default 1 (1 unlike, 2 like, 3 downloading, 4 done)")
	resetCmd.StringVar(&cmd_dbfile, "db", "", "special dbfile for query.")

	// 子命令 inspect
	inspectCmd := flag.NewFlagSet("inspect", flag.ExitOnError)
	inspectCmd.StringVar(&cmd_dbfile, "db", "", "special dbfile for query.")

	if len(os.Args) < 2 {
		dbfile = get_dbfile(cmd_dbfile)
		DBdriver.QueryStatusCount(dbfile)
		os.Exit(0)
	}

	switch os.Args[1] {
	case "show":
		showCmd.Parse(os.Args[2:])
		dbfile = get_dbfile(cmd_dbfile)
		DBdriver.QueryStatusCount(dbfile)
		// -d
		showDownloadingMovies(isShowDownloading, dbfile)
		// -i
		showUnlikedMovies(limit, dbfile)
		// -w
		showDoneMovies(showDoneBylimit, dbfile)
	case "reset":
		resetCmd.Parse(os.Args[2:])
		dbfile = get_dbfile(cmd_dbfile)
		setStatus(resetCmd.Args(), dest_status, dbfile)
		// reset status
	case "inspect":
		inspectCmd.Parse(os.Args[2:])
		dbfile = get_dbfile(cmd_dbfile)
		showDetailmovie(inspectCmd.Args(), dbfile)
	case "-h", "--help":
		showCmd.Usage()
		resetCmd.Usage()
		inspectCmd.Usage()
	default:
		fmt.Println("Unknow cmd:", os.Args[1])
		showCmd.Usage()
		resetCmd.Usage()
		inspectCmd.Usage()
	}
}
