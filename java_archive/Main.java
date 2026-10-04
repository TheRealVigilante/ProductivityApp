import java.io.IOException;
import java.util.Scanner;

public class Main {
        public static class ClassSelector {
        public static void selectClass(int choice) throws IOException, InterruptedException {
            switch (choice) {
                case 1:
                    Scanner scanner = new Scanner(System.in);
                    System.out.println("Enter the name of this block:");
                    String listName = scanner.nextLine();
                    System.out.println("Choose an option for Create Block:");
                    System.out.println("a. Block for a time");
                    System.out.println("b. Block After");
                    System.out.println("c. Set A daily Limit");
                    System.out.println("d. Set password");

                    char blockChoice = scanner.next().charAt(0);
                    BlacklistGUI blacklist = new BlacklistGUI();
                    blacklist.launchGUI(listName);
                    blacklist.waitForSubmit();
                    String[] files= Applications.AbsoluteFinder().toArray(new String[0]);
                    switch (blockChoice) {
                        case 'a':
                            CountdownTimerGUI.Time(files, listName);
                            break;
                        case 'b':
                            CountdownTimerGUI.AfterTime(files, listName);
                            break;
                        case 'c':
                            DailyLimitLock.DailyLock(files,listName);
                            break;
                        case 'd':
                            PasswordGUI.PasswordLock(files,listName);
                            break;
                        default:
                            System.out.println("Invalid option for Create Block");
                            break;
                    }
                    break;
                case 2:
                    System.out.println("Edit Block is Under Development");
                    System.exit(0);
                    break;
                case 3:
                    System.out.println("Choose an option for Create Deadlock:");
                    System.out.println("a. Block for a time");
                    System.out.println("b. Block After");
                    System.out.println("c. Set a daily Limit");
                    System.out.println("d. Set password(Under Devolopment)");
                    Scanner scanner2 = new Scanner(System.in);
                    char deadlockChoice = scanner2.next().charAt(0);
                    switch (deadlockChoice) {
                        case 'a':
                            Deadlock.TimerDeadlock();
                            break;
                        case 'b':
                            Deadlock.AfterTimerDeadlock();
                            break;
                        case 'c':
//                            Deadlock.DailyDeadlock();
                            System.out.println("Under Development");
                            System.exit(0);
                            break;
                        case 'd':
                            Deadlock.PassDeadlock();
                            break;
                        default:
                            System.out.println("Invalid option for Create Deadlock");
                            break;
                    }
                    break;
                default:
                    System.out.println("Invalid choice");
                    break;
            }
        }
    }


    public static void main(String[] args) throws IOException, InterruptedException {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Choose a number:");
        System.out.println("1. Create Block");
        System.out.println("2. Edit Block (Under Development)");
        System.out.println("3. Create Deadlock");

        int choice = scanner.nextInt();
        ClassSelector.selectClass(choice);
        scanner.close();
    }
}
